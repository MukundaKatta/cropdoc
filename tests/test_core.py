"""Tests for Cropdoc."""
from src.core import Cropdoc
def test_init(): assert Cropdoc().get_stats()["ops"] == 0
def test_op(): c = Cropdoc(); c.detect(x=1); assert c.get_stats()["ops"] == 1
def test_multi(): c = Cropdoc(); [c.detect() for _ in range(5)]; assert c.get_stats()["ops"] == 5
def test_reset(): c = Cropdoc(); c.detect(); c.reset(); assert c.get_stats()["ops"] == 0
def test_service_name(): c = Cropdoc(); r = c.detect(); assert r["service"] == "cropdoc"
