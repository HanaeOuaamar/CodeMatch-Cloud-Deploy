import streamlit as st
import torch
import torch.nn as nn
import unicodedata
import re
import math
from tokenizers import Tokenizer
from tokenizers.models import BPE
from tokenizers.trainers import BpeTrainer
from tokenizers.pre_tokenizers import Whitespace
import requests
import time
import os

# Configuration de la page
st.set_page_config(
    page_title="Tokenization & Embeddings Workshop",
    page_icon="📚",
    layout="wide"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
    }
    .success-box {
        background: #d4edda;
        border: 1px solid #c3e6cb;
        padding: 1rem;
        border-radius: 8px;
        color: #155724;
    }
    .warning-box {
        background: #fff3cd;
        border: 1px solid #ffeaa7;
        padding: 1rem;
        border-radius: 8px;
        color: #856404;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>📚 Build an LLM from Scratch: Part II</h1>
    <p>Tokenization and Embeddings Workshop - Entraînement sur Shakespeare</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'shakespeare_text' not in st.session_state:
    st.session_state.shakespeare_text = None
if 'tokenizer' not in st.session_state:
    st.session_state.tokenizer = None
if 'tokenizer_trained' not in st.session_state:
    st.session_state.tokenizer_trained = False
if 'data_stats' not in st.session_state:
    st.session_state.data_stats = None
if 'train_data' not in st.session_state:
    st.session_state.train_data = None
if 'val_data' not in st.session_state:
    st.session_state.val_data = None

# Sidebar - Configuration
st.sidebar.header("⚙️ Configuration")
vocab_size = st.sidebar.number_input("Vocabulary Size", min_value=1000, max_value=10000, value=5000, step=500)
d_model = st.sidebar.number_input("d_model (Embedding Dimension)", min_value=128, max_value=1024, value=512, step=128)
max_len = st.sidebar.number_input("Max Sequence Length", min_value=64, max_value=512, value=256, step=64)
batch_size = st.sidebar.number_input("Batch Size", min_value=8, max_value=64, value=32, step=8)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📋 Pipeline Steps")
st.sidebar.markdown("""
1. ✅ Load Shakespeare Dataset
2. ✅ Train BPE Tokenizer
3. ✅ Create Embeddings
4. ✅ Test Transformer Pass
""")

# Fonctions utilitaires
@st.cache_data
def load_shakespeare_dataset():
    """Télécharge et analyse le dataset Shakespeare"""
    try:
        url = "https://raw.githubusercontent.com/karpathy/char-rnn/master/data/tinyshakespeare/input.txt"
        response = requests.get(url)
        text = response.text
        
        # Statistiques
        stats = {
            'total_chars': len(text),
            'letters': sum(c.isalpha() for c in text),
            'spaces': sum(c.isspace() for c in text),
            'punctuation': sum(c in '.,;:!?\'"()-' for c in text),
            'lines': len(text.split('\n')),
            'words': len(text.split())
        }
        
        return text, stats
    except Exception as e:
        st.error(f"Erreur lors du chargement: {e}")
        return None, None

def preprocess_for_bpe_training(text):
    """Prétraite le texte pour l'entraînement BPE"""
    # Normalisation Unicode
    text = unicodedata.normalize('NFC', text)
    
    # Séparer la ponctuation
    text = re.sub(r"([!?,.:;])", r" \1 ", text)
    
    # Gérer les apostrophes
    text = re.sub(r"\b(l'|d'|n'|s'|t'|m'|j'|c')", r"\1 ", text, flags=re.IGNORECASE)
    text = re.sub(r"\b(aujourd'|presqu'|quelqu')", r"\1 ", text, flags=re.IGNORECASE)
    
    # Normaliser les espaces
    text = re.sub(r'\s+', ' ', text)
    
    # Gérer les sauts de ligne
    lines = text.split('\n')
    lines = [line.strip() for line in lines]
    text = '\n'.join(lines)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    return text

def train_bpe_tokenizer(text, vocab_size):
    """Entraîne le tokenizer BPE"""
    # Initialiser le tokenizer
    tokenizer = Tokenizer(BPE(unk_token="[UNK]"))
    tokenizer.pre_tokenizer = Whitespace()
    
    # Configurer l'entraîneur
    trainer = BpeTrainer(vocab_size=vocab_size, special_tokens=["[UNK]"])
    
    # Entraîner
    tokenizer.train_from_iterator(text.split('\n'), trainer=trainer)
    
    return tokenizer

def create_positional_encoding(d_model, max_len):
    """Crée la matrice de positional encoding"""
    pe = torch.zeros(max_len, d_model)
    position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
    div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
    
    pe[:, 0::2] = torch.sin(position * div_term)
    pe[:, 1::2] = torch.cos(position * div_term)
    pe = pe.unsqueeze(0)
    
    return pe

# Tabs principales
tab1, tab2, tab3, tab4 = st.tabs(["📥 Load Dataset", "🔧 Train Tokenizer", "🎯 Embeddings", "🚀 Transformer Test"])

# TAB 1: Load Dataset
with tab1:
    st.header("📥 Charger le Dataset Shakespeare")
    
    st.info("💡 Ce dataset contient les œuvres complètes de Shakespeare et sera utilisé pour entraîner notre tokenizer BPE.")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.button("📥 Télécharger le Dataset", type="primary", use_container_width=True):
            with st.spinner("Téléchargement en cours..."):
                text, stats = load_shakespeare_dataset()
                if text:
                    st.session_state.shakespeare_text = text
                    st.session_state.data_stats = stats
                    st.success("✅ Dataset chargé avec succès!")
    
    if st.session_state.shakespeare_text:
        st.markdown("### 📊 Statistiques du Dataset")
        
        # Afficher les métriques
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Caractères", f"{st.session_state.data_stats['total_chars']:,}")
        with col2:
            st.metric("Mots", f"{st.session_state.data_stats['words']:,}")
        with col3:
            st.metric("Lignes", f"{st.session_state.data_stats['lines']:,}")
        with col4:
            st.metric("Lettres", f"{st.session_state.data_stats['letters']:,}")
        
        # Composition du texte
        st.markdown("### 📈 Composition du Texte")
        col1, col2, col3 = st.columns(3)
        
        total = st.session_state.data_stats['total_chars']
        
        with col1:
            letters_pct = (st.session_state.data_stats['letters'] / total * 100)
            st.metric("Lettres", f"{letters_pct:.1f}%")
        with col2:
            spaces_pct = (st.session_state.data_stats['spaces'] / total * 100)
            st.metric("Espaces", f"{spaces_pct:.1f}%")
        with col3:
            punct_pct = (st.session_state.data_stats['punctuation'] / total * 100)
            st.metric("Ponctuation", f"{punct_pct:.1f}%")
        
        # Aperçu du texte
        st.markdown("### 👀 Aperçu du Texte")
        st.text_area("Premiers 500 caractères", 
                     st.session_state.shakespeare_text[:500] + "...", 
                     height=150,
                     disabled=True)



# TAB 3: Embeddings
with tab3:
    st.header("🎯 Créer les Embeddings")
    
    if not st.session_state.tokenizer_trained:
        st.warning("⚠️ Veuillez d'abord entraîner le tokenizer depuis l'onglet 'Train Tokenizer'")
    else:
        st.info("💡 Les embeddings transforment les tokens (nombres entiers) en vecteurs denses qui capturent leur sens sémantique.")
        
        if st.button("🎯 Générer les Embeddings", type="primary", use_container_width=True):
            with st.spinner("Génération des embeddings..."):
                # Créer les couches
                device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
                
                # Token embedding layer
                token_embedding = nn.Embedding(vocab_size, d_model).to(device)
                
                # Positional encoding
                pe_matrix = create_positional_encoding(d_model, max_len).to(device)
                
                # Dropout
                dropout = nn.Dropout(p=0.1).to(device)
                
                # Créer un batch d'exemple
                sample_ids = torch.randint(0, vocab_size, (batch_size, max_len)).to(device)
                
                # Forward pass
                token_embeds = token_embedding(sample_ids) * math.sqrt(d_model)
                final_embeds = token_embeds + pe_matrix[:, :max_len]
                final_embeds = dropout(final_embeds)
                
                st.success("✅ Embeddings générés avec succès!")
                
                # Afficher les informations
                st.markdown("### 📐 Dimensions des Embeddings")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Token Embedding", f"[{batch_size}, {max_len}, {d_model}]")
                with col2:
                    st.metric("Positional Encoding", f"[1, {max_len}, {d_model}]")
                with col3:
                    st.metric("Final Embedding", f"[{batch_size}, {max_len}, {d_model}]")
                
                # Pipeline
                st.markdown("### 🔄 Pipeline des Embeddings")
                st.code("""
Token IDs → Embedding Layer → × √d_model → + Positional Encoding → Dropout → Ready for Transformer
                """)
                
                # Afficher un échantillon
                st.markdown("### 📊 Échantillon des Embeddings (5x5)")
                sample_array = final_embeds[0, :5, :5].detach().cpu().numpy()
                st.dataframe(sample_array, use_container_width=True)
                
                # Paramètres
                total_params = vocab_size * d_model
                st.markdown(f"**Paramètres de l'embedding layer:** {total_params:,}")

# TAB 4: Transformer Test
with tab4:
    st.header("🚀 Test du Passage Transformer")
    
    if not st.session_state.tokenizer_trained:
        st.warning("⚠️ Veuillez d'abord entraîner le tokenizer et générer les embeddings")
    else:
        st.info("💡 Vérifions que nos embeddings ont la bonne forme pour passer dans un bloc Transformer.")
        
        if st.button("🚀 Tester le Transformer", type="primary", use_container_width=True):
            with st.spinner("Test en cours..."):
                device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
                
                # Créer les embeddings
                token_embedding = nn.Embedding(vocab_size, d_model).to(device)
                pe_matrix = create_positional_encoding(d_model, max_len).to(device)
                dropout = nn.Dropout(p=0.1).to(device)
                
                # Créer un batch d'exemple
                sample_ids = torch.randint(0, vocab_size, (batch_size, max_len)).to(device)
                
                # Forward pass pour les embeddings
                token_embeds = token_embedding(sample_ids) * math.sqrt(d_model)
                final_embeds = token_embeds + pe_matrix[:, :max_len]
                final_embeds = dropout(final_embeds)
                
                # Créer un transformer block
                transformer_block = nn.TransformerEncoderLayer(
                    d_model=d_model,
                    nhead=8,
                    batch_first=True
                ).to(device)
                
                try:
                    # Passer dans le transformer
                    output = transformer_block(final_embeds)
                    
                    st.success("✅ Test réussi! Les embeddings passent correctement dans le Transformer.")
                    st.balloons()
                    
                    # Afficher les résultats
                    st.markdown("### ✅ Validation Réussie")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**Input Shape:**")
                        st.code(f"torch.Size([{batch_size}, {max_len}, {d_model}])")
                    
                    with col2:
                        st.markdown("**Output Shape:**")
                        st.code(f"torch.Size({list(output.shape)})")
                    
                    # Checklist
                    st.markdown("### ✅ Checklist de Validation")
                    st.markdown("""
                    - ✅ Dimension d'embedding correspond à d_model
                    - ✅ Longueur de séquence dans les limites max_len
                    - ✅ Dimension de batch correctement configurée
                    - ✅ Prêt pour multi-head attention
                    - ✅ Format compatible avec PyTorch Transformer
                    """)
                    
                    # Configuration du transformer
                    st.markdown("### ⚙️ Configuration du Transformer")
                    config_col1, config_col2, config_col3 = st.columns(3)
                    
                    with config_col1:
                        st.metric("d_model", d_model)
                    with config_col2:
                        st.metric("n_heads", 8)
                    with config_col3:
                        st.metric("batch_first", "True")
                    
                except Exception as e:
                    st.error(f"❌ Erreur lors du passage dans le Transformer: {e}")

# Footer
st.markdown("---")
st.markdown("""
### 📚 Résumé du Workshop
Ce notebook vous a permis de :
1. ✅ Charger et analyser le dataset Shakespeare
2. ✅ Entraîner un tokenizer BPE sur le corpus
3. ✅ Créer des embeddings (token + positional)
4. ✅ Valider le passage dans un bloc Transformer

**Prochaines étapes:** Entraîner un modèle de langage complet avec ces composants!
""")