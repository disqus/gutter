import com.twitter.common.zookeeper.ZooKeeperMap
import com.twitter.common.zookeeper.ZooKeeperClient
import com.twitter.common.quantity.Amount
import com.twitter.common.quantity.Time

import com.google.common.base.Function


class PassThroughDeserializer extends Function[Array[Byte],String] {
    def apply(bytes: Array[Byte]): String = bytes.toString
}

object Client {
    def main(args: Array[String]): Unit = {
        val address = new java.net.InetSocketAddress("127.0.0.1", 2181)
        val timeout = Amount.of(30, Time.SECONDS)
        val client = new ZooKeeperClient(timeout, address)

        val deserializer = new PassThroughDeserializer

        val switches = ZooKeeperMap.create(client, "hackweek", deserializer)
    }
}