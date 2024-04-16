# Copyright 2022 Red Hat Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Clowder integration functions."""
import logging

import yaml
import app_common_python
from app_common_python.types import BrokerConfigAuthtypeEnum


logger = logging.getLogger(__name__)


def apply_clowder_config(manifest):
    """Apply Clowder config values to ICM config manifest."""
    Loader = getattr(yaml, "CSafeLoader", yaml.SafeLoader)
    config = yaml.load(manifest, Loader=Loader)

    _add_kafka_config(config)
    _add_buckets_config(config)

    return config


def _add_kafka_config(config):
    # Find the Payload Tracker watcher, as it might be affected by config changes
    logger = logging.getLogger(__name__)
    pt_watcher_name = "ccx_messaging.watchers.payload_tracker_watcher.PayloadTrackerWatcher"
    pt_watcher = None
    for watcher in config["service"]["watchers"]:
        if watcher["name"] == pt_watcher_name:
            pt_watcher = watcher
            break

    clowder_broker_config = app_common_python.LoadedConfig.kafka.brokers[0]
    kafka_urls = app_common_python.KafkaServers
    logger.debug("Kafka URLs: %s", kafka_urls)

    kafka_broker_config = {"bootstrap.servers": ",".join(kafka_urls)}

    if clowder_broker_config.cacert:
        # Current Kafka library is not able to handle the CA file, only a path to it
        # FIXME: Duplicating parameters in order to be used by both Kafka libraries
        ssl_ca_location = app_common_python.LoadedConfig.kafka_ca()
        kafka_broker_config["ssl.ca.location"] = ssl_ca_location

    if BrokerConfigAuthtypeEnum.valueAsString(clowder_broker_config.authtype) == "sasl":
        kafka_broker_config.update(
            {
                "sasl.mechanisms": clowder_broker_config.sasl.saslMechanism,
                "sasl.username": clowder_broker_config.sasl.username,
                "sasl.password": clowder_broker_config.sasl.password,
                "security.protocol": clowder_broker_config.sasl.securityProtocol,
            }
        )

    config["service"]["consumer"].setdefault(
        "kwargs", {})["kafka_broker_config"] = kafka_broker_config
    config["service"]["publisher"].setdefault(
        "kwargs", {})["kafka_broker_config"] = kafka_broker_config

    if pt_watcher:
        pt_watcher["kwargs"]["kafka_broker_config"] = kafka_broker_config

    logger.info("Kafka configuration updated from Clowder configuration")

    consumer_topic = config["service"]["consumer"]["kwargs"].get("incoming_topic")
    dlq_topic = config["service"]["consumer"]["kwargs"].get("dead_letter_queue_topic")
    producer_topic = config["service"]["publisher"]["kwargs"].get("outgoing_topic")
    payload_tracker_topic = pt_watcher["kwargs"].pop("topic") if pt_watcher else None

    if consumer_topic in app_common_python.KafkaTopics:
        topic_cfg = app_common_python.KafkaTopics[consumer_topic]
        config["service"]["consumer"]["kwargs"]["incoming_topic"] = topic_cfg.name
    else:
        logger.warn("The consumer topic cannot be found in Clowder mapping. It can cause errors")

    if dlq_topic in app_common_python.KafkaTopics:
        topic_cfg = app_common_python.KafkaTopics[dlq_topic]
        config["service"]["consumer"]["kwargs"]["dead_letter_queue_topic"] = topic_cfg.name

    if producer_topic in app_common_python.KafkaTopics:
        topic_cfg = app_common_python.KafkaTopics[producer_topic]
        config["service"]["publisher"]["kwargs"]["outgoing_topic"] = topic_cfg.name
    else:
        logger.warn("The publisher topic cannot be found in Clowder mapping. It can cause errors")

    if pt_watcher and payload_tracker_topic in app_common_python.KafkaTopics:
        topic_cfg = app_common_python.KafkaTopics[payload_tracker_topic]
        pt_watcher["kwargs"]["topic"] = topic_cfg.name
    else:
        logger.warn(
            "The Payload Tracker watcher topic cannot be found in Clowder mapping. "
            "It can cause errors",
        )

def _add_buckets_config(config):
    logger = logging.getLogger(__name__)
    buckets = app_common_python.ObjectBuckets

    logger.info("Buckets: %s", buckets)
    logger.info("Loaded config %s", app_common_python.LoadedConfig.objectStore)
    logger.info("Downloader config: %s", config["service"]["downloader"])
    logger.info("Engine config: %s", config["service"]["engine"])
