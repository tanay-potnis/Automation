#!/usr/bin/expect

echo "Initiating Install.."

set timeout -1
set IdracUser: "root"
set IdracPassword: "calvin"
set IdracIP: "10.9.18.235"

spawn ssh root@10.9.18.235

expect "(yes/no)?" {
	send "yes\r"
	expect "*?assword" { send "adminadmin\r" }
	} "*?assword" { send "adminadmin\r" }


