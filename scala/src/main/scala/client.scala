import com.twitter.common.zookeeper.ZooKeeperMap
import com.twitter.common.zookeeper.ZooKeeperClient
import com.twitter.common.quantity.Amount
import com.twitter.common.quantity.Time

import com.google.common.base.Function

import gutter.Interfaces;


class SwitchDeserializer extends Function[Array[Byte],Interfaces.Switch] {
    def apply(bytes: Array[Byte]) = Interfaces.Switch.parseFrom(bytes)
}

object Client {

    val DOGE = """wow. many consistency. very demo.
─────────▄──────────────▄
────────▌▒█───────────▄▀▒▌
────────▌▒▒▀▄───────▄▀▒▒▒▐
───────▐▄▀▒▒▀▀▀▀▄▄▄▀▒▒▒▒▒▐
─────▄▄▀▒▒▒▒▒▒▒▒▒▒▒█▒▒▄█▒▐
───▄▀▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▀██▀▒▌
──▐▒▒▒▄▄▄▒▒▒▒▒▒▒▒▒▒▒▒▒▀▄▒▒▌
──▌▒▒▐▄█▀▒▒▒▒▄▀█▄▒▒▒▒▒▒▒█▒▐
─▐▒▒▒▒▒▒▒▒▒▒▒▌██▀▒▒▒▒▒▒▒▒▀▄▌
─▌▒▀▄██▄▒▒▒▒▒▒▒▒▒▒▒░░░░▒▒▒▒▌
─▌▀▐▄█▄█▌▄▒▀▒▒▒▒▒▒░░░░░░▒▒▒▐
▐▒▀▐▀▐▀▒▒▄▄▒▄▒▒▒▒▒░░░░░░▒▒▒▒▌
▐▒▒▒▀▀▄▄▒▒▒▄▒▒▒▒▒▒░░░░░░▒▒▒▐
─▌▒▒▒▒▒▒▀▀▀▒▒▒▒▒▒▒▒░░░░▒▒▒▒▌
─▐▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▐
──▀▄▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▄▒▒▒▒▌
────▀▄▒▒▒▒▒▒▒▒▒▒▄▄▄▀▒▒▒▒▄▀
───▐▀▒▀▄▄▄▄▄▄▀▀▀▒▒▒▒▒▄▄▀
──▐▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▀▀"""

    val address = new java.net.InetSocketAddress("127.0.0.1", 2181)
    val timeout = Amount.of(30, Time.SECONDS)
    val client = new ZooKeeperClient(timeout, address)

    val deserializer = new SwitchDeserializer

    val switches = ZooKeeperMap.create(client, "/hackweek", deserializer)

    var last: List[String] = null
    val random = scala.util.Random
    var age = random.nextInt(99) + 1

    def main(args: Array[String]): Unit = {
        while (true) {
            handleNode(switches.get("default.doge"))
            Thread.sleep(1000)
        }
    }

    def handleNode(switch: Interfaces.Switch) = {
        val conditions = switch.getConditions.getConditionsList
        val operator = conditions.get(0).getOperator.split(":")

        val matches = operator(0) match {
            case "equals" if operator(1).toInt == age => true
            case "between" if operator(1).toInt < age && operator(2).toInt >age => true
            case "more_than" if operator(1).toInt < age => true
            // LOL TYPO
            case "before" if operator(1).toInt > age => true
            case _ => false
        }

        if (last != null && operator(0) == "equals" && matches == true && last != operator.toList) {
            println(DOGE)
            println("YOU WIN! SUCH " + age.toString + " AGE. WOW.")
            age = random.nextInt(99) + 1
        } else if (last != null && matches == true && last != operator.toList) {
            println("Yes: " + conditions.get(0).getOperator)
        } else if (last != null && matches == false && last != operator.toList) {
            println("No: " + conditions.get(0).getOperator)
        }

        last = operator.toList
    }
}