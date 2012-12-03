from test_integration import TestIntegration
from noseperf.testcases import PerformanceTest

from redis import Redis
from modeldict.redis import RedisDict

from exam.decorators import before, fixture

from gutter.client.models import Manager


class TestPerformance(TestIntegration, PerformanceTest):

    @before
    def switch_to_redis_backend(self):
        pass

    @fixture
    def redis(self):
        return Redis()

    @before
    def flush_redis(self):
        self.redis.flushdb()

    @fixture
    def manager(self):
        return Manager(storage=RedisDict('gutter-tests', self.redis))
