from __future__ import annotations

import hashlib
import os
import time
import uuid
from dataclasses import dataclass
from typing import Any, AsyncIterator, Dict, Optional

import orjson
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer


def _now_ms() -> int:
    return int(time.time() * 1000)


def stable_sha256_hex(*parts: str) -> str:
    h = hashlib.sha256()
    for p in parts:
        h.update(p.encode("utf-8"))
        h.update(b"\x1f")
    return h.hexdigest()


def make_envelope(
    *,
    event_type: str,
    scan_id: str,
    correlation_id: str,
    idempotency_key: str,
    payload: Dict[str, Any],
    schema_version: str = "1.0",
) -> Dict[str, Any]:
    return {
        "schema_version": schema_version,
        "event_type": event_type,
        "scan_id": scan_id,
        "correlation_id": correlation_id,
        "idempotency_key": idempotency_key,
        "produced_at_ms": _now_ms(),
        "payload": payload,
    }


def dumps(obj: Any) -> bytes:
    return orjson.dumps(obj)


def loads(data: bytes) -> Any:
    return orjson.loads(data)


@dataclass
class KafkaClients:
    producer: AIOKafkaProducer


async def make_producer(bootstrap_servers: str, client_id: str) -> AIOKafkaProducer:
    base_kwargs = dict(
        bootstrap_servers=bootstrap_servers,
        client_id=client_id,
        acks="all",
        linger_ms=5,
        value_serializer=dumps,
        key_serializer=lambda k: k.encode("utf-8") if isinstance(k, str) else k,
    )

    # aiokafka's constructor arguments have changed across versions.
    # We prefer idempotence when supported, but we must stay compatible.
    try:
        producer = AIOKafkaProducer(
            **base_kwargs,
            enable_idempotence=True,
        )
    except TypeError:
        producer = AIOKafkaProducer(
            **base_kwargs,
        )
    await producer.start()
    return producer


async def make_consumer(
    *,
    topic: str,
    bootstrap_servers: str,
    group_id: str,
    client_id: str,
) -> AIOKafkaConsumer:
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id=group_id,
        client_id=f"{client_id}-{group_id}",
        enable_auto_commit=False,
        auto_offset_reset=os.getenv("KAFKA_OFFSET_RESET", "earliest"),
        value_deserializer=loads,
    )
    await consumer.start()
    return consumer


def new_correlation_id() -> str:
    return str(uuid.uuid4())
