#!/bin/sh



action="-I"
# action="-D"

external_ip='94.23.12.84'
external_if='eth0'

backend_ip='192.168.123.200'
frontend_ip='192.168.123.201'

iptables -t nat $action PREROUTING -d ${external_ip} -i ${external_if} -p tcp -m tcp \
    --dport 2222 -j DNAT --to-destination ${frontend_ip}:22

iptables -t nat $action PREROUTING -d ${external_ip} -i ${external_if} -p tcp -m tcp \
    --dport 8080 -j DNAT --to-destination ${frontend_ip}:8080

#iptables -t nat $action PREROUTING -d ${external_ip} -i ${external_if} -p tcp -m tcp \
#    --dport 80 -j DNAT --to-destination ${frontend_ip}:80

iptables -t nat $action PREROUTING -d ${external_ip} -i ${external_if} -p tcp -m tcp \
    --dport 2223 -j DNAT --to-destination ${backend_ip}:22


iptables $action FORWARD -d ${frontend_ip} -p tcp -m state --state NEW -m tcp --dport 22 -j ACCEPT
iptables $action FORWARD -d ${frontend_ip} -p tcp -m state --state NEW -m tcp --dport 8080 -j ACCEPT
# iptables $action FORWARD -d ${frontend_ip} -p tcp -m state --state NEW -m tcp --dport 80 -j ACCEPT
iptables $action FORWARD -d ${backend_ip}  -p tcp -m state --state NEW -m tcp --dport 22 -j ACCEPT
