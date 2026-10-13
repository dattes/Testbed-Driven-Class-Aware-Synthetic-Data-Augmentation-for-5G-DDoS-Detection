#!/usr/bin/env python3

"""
     >>> Mininet topology <<<

              (Free5GC)
               ctrl-vm
                  |
(UERANSIM)        |            (UPF)
    h1 ---------- r0 ---------- h2
                  |             |
                  h4            r1 
             (adversary)        |
                                |
                                h3
                               (DN)


- 192.168.1.0/24
    h1-eth0 192.168.1.1/24
    r0-eth0 192.168.1.254/24
- 192.168.2.0/24
    h2-eth0 192.168.2.2/24
    r0-eth1 192.168.2.254/24
- 192.168.3.0/24
    h3-eth0 192.168.3.3/24
    r1-eth1 192.168.3.254/24
- 192.168.4.0/24
    h4-eth0 192.168.4.4/24
    r0-eth2 192.168.4.254/24
- 192.168.5.0/24
    h2-eth1 192.168.5.5/24
    r1-eth0 192.168.5.254/24
"""

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node, OVSBridge
from mininet.nodelib import NAT
from mininet.log import setLogLevel, info
from mininet.cli import CLI

SL24 = '/24'

# UE/RAN (h1)
NET1   = '192.168.1.0' + SL24
H1_IP4 = '192.168.1.1'
H1_MAC = '00:00:00:00:01:01'
TUN   = '10.60.0.0' + SL24
H1_TUN_IP4 = '10.60.0..1'

# UPF (h2)
NET2   = '192.168.2.0' + SL24
H2_IP4 = '192.168.2.2'
H2_MAC = '00:00:00:00:02:02'

NET5   = '192.168.5.0' + SL24
H5_IP4 = '192.168.5.5'
H5_MAC = '00:00:00:00:05:05'

# Router 0 (r0)
R0_N1_IP4 = '192.168.1.254'
R0_N1_MAC = '00:00:00:00:01:a0'
R0_N2_IP4 = '192.168.2.254'
R0_N2_MAC = '00:00:00:00:02:a0'
R0_N4_IP4 = '192.168.4.254'
R0_N4_MAC = '00:00:00:00:04:a0'

# Router 1 (r1)
R1_N3_IP4 = '192.168.3.254'
R1_N3_MAC = '00:00:00:00:03:a0'
R1_N5_IP4 = '192.168.5.254'
R1_N5_MAC = '00:00:00:00:05:a0'

# Data Network (h3)
NET3   = '192.168.3.0' + SL24
H3_IP4 = '192.168.3.3'
H3_MAC = '00:00:00:00:03:03'

# Adversary (h4)
NET4   = '192.168.4.0' + SL24
H4_IP4 = '192.168.4.4'
H4_MAC = '00:00:00:00:04:04'


class LinuxRouter( Node ):

    # Enable IPv4 forwarding
    def config( self, **params ):
        super( LinuxRouter, self).config( **params )
        self.cmd( 'sysctl net.ipv4.ip_forward=1' )

    def terminate( self ):
        self.cmd( 'sysctl net.ipv4.ip_forward=0' )
        super( LinuxRouter, self ).terminate()

# Network topology with 5 IP subnets: (h1-r0), (h2-r0), (h4-r0), (h2-r1) and (h3-r1)
class NetworkTopo( Topo ):

    def build( self, **_opts ):
        r0 = self.addNode( 'r0', cls=LinuxRouter, inNamespace=False, ip=R0_N1_IP4+SL24, mac=R0_N1_MAC )
        r1 = self.addNode( 'r1', cls=LinuxRouter, ip=R1_N5_IP4+SL24, mac=R1_N5_MAC )

        h1 = self.addHost( 'h1', ip=H1_IP4+SL24, mac=H1_MAC )
        h2 = self.addHost( 'h2', ip=H2_IP4+SL24, mac=H2_MAC )
        h3 = self.addHost( 'h3', ip=H3_IP4+SL24, mac=H3_MAC )
        h4 = self.addHost( 'h4', ip=H4_IP4+SL24, mac=H4_MAC )

        self.addLink( h1, r0, intfName1='h1-eth0', intfName2='r0-eth0' )
        self.addLink( h2, r0, intfName1='h2-eth0', intfName2='r0-eth1' )
        self.addLink( h4, r0, intfName1='h4-eth0', intfName2='r0-eth2' )

        self.addLink( h2, r1, intfName1='h2-eth1', intfName2='r1-eth0' )
        self.addLink( h3, r1, intfName1='h3-eth0', intfName2='r1-eth1' )


def config(net):
    # In external VM (ctrl-vm)
    info( '\n*** Run the following commands in the external VM:\n' )
    info( 'sudo ip route add 192.168.1.0/24 via 192.168.56.20 dev enp0s8\n' )
    info( 'sudo ip route add 192.168.2.0/24 via 192.168.56.20 dev enp0s8\n' )
    info( 'sudo ip route add 192.168.4.0/24 via 192.168.56.20 dev enp0s8\n' )

    # Interfaces
    net.get('r0').cmd('ip l set dev r0-eth1 address %s' % R0_N2_MAC)
    net.get('r0').cmd('ip l set dev r0-eth2 address %s' % R0_N4_MAC)
    net.get('r0').cmd('ip a add %s dev r0-eth1' % (R0_N2_IP4+SL24))
    net.get('r0').cmd('ip a add %s dev r0-eth2' % (R0_N4_IP4+SL24))

    net.get('r1').cmd('ip l set dev r1-eth0 address %s' % R1_N5_MAC)
    net.get('r1').cmd('ip l set dev r1-eth1 address %s' % R1_N3_MAC)
    net.get('r1').cmd('ip a add %s dev r1-eth0' % (R1_N5_IP4+SL24))
    net.get('r1').cmd('ip a add %s dev r1-eth1' % (R1_N3_IP4+SL24))

    net.get('h2').cmd('ip a add %s dev h2-eth1' % (H5_IP4+SL24))

    # Neighbors
    net.get('h1').cmd('ip nei add %s lladdr %s dev h1-eth0' % (R0_N1_IP4, R0_N1_MAC))
    net.get('r0').cmd('ip nei add %s lladdr %s dev r0-eth0' % (H1_IP4, H1_MAC))

    net.get('h2').cmd('ip nei add %s lladdr %s dev h2-eth0' % (R0_N2_IP4, R0_N2_MAC))
    net.get('r0').cmd('ip nei add %s lladdr %s dev r0-eth1' % (H2_IP4, H2_MAC))

    net.get('h4').cmd('ip nei add %s lladdr %s dev h4-eth0' % (R0_N4_IP4, R0_N4_MAC))
    net.get('r0').cmd('ip nei add %s lladdr %s dev r0-eth2' % (H4_IP4, H4_MAC))

    net.get('h2').cmd('ip nei add %s lladdr %s dev h2-eth1' % (R1_N5_IP4, R1_N5_MAC))
    net.get('r1').cmd('ip nei add %s lladdr %s dev r1-eth0' % (H2_IP4, H2_MAC))

    net.get('h3').cmd('ip nei add %s lladdr %s dev h3-eth0' % (R1_N3_IP4, R1_N3_MAC))
    net.get('r1').cmd('ip nei add %s lladdr %s dev r1-eth1' % (H3_IP4, H3_MAC))

    # Routes
    net.get('h1').cmd('ip r add default via %s dev h1-eth0' % R0_N1_IP4)
    net.get('h2').cmd('ip r add default via %s dev h2-eth0' % R0_N2_IP4)
    net.get('h3').cmd('ip r add default via %s dev h3-eth0' % R1_N3_IP4)
    net.get('h4').cmd('ip r add default via %s dev h4-eth0' % R0_N4_IP4)

    net.get('h1').cmd('ip r add %s via %s dev h1-eth0' % (NET2, R0_N1_IP4))

    net.get('h2').cmd('ip r add %s via %s dev h2-eth0' % (NET1, R0_N2_IP4))
    net.get('h2').cmd('ip r add %s via %s dev h2-eth1' % (NET3, R1_N5_IP4))

    net.get('h3').cmd('ip r add %s via %s dev h3-eth0' % (NET5, R1_N3_IP4))

    net.get('r0').cmd('ip r add %s via %s dev r0-eth1' % (NET3, H2_IP4))

    net.get('r1').cmd('ip r add %s via %s dev r1-eth0' % (NET1, H5_IP4))
    net.get('r1').cmd('ip r add %s via %s dev r1-eth0' % (NET2, H5_IP4))
    net.get('r1').cmd('ip r add %s via %s dev r1-eth0' % (NET4, H5_IP4))
    net.get('r1').cmd('ip r add %s via %s dev r1-eth0' % (TUN, H5_IP4))

    net.get('h1').cmd('ip r add %s dev uesimtun0' % (NET3))
    
    # Forward
    net.get('h2').cmd('sysctl -w net.ipv4.ip_forward=1')
    net.get('h2').cmd('iptables -P FORWARD ACCEPT')

    net.get('r0').cmd('sysctl -w net.ipv4.ip_forward=1')
    net.get('r0').cmd('iptables -t nat -A POSTROUTING -s 192.168.4.0/24 -o enp0s8 -j MASQUERADE')
    net.get('r0').cmd('iptables -t nat -A POSTROUTING -s 192.168.2.0/24 -o enp0s8 -j MASQUERADE')
    net.get('r0').cmd('iptables -t nat -A POSTROUTING -s 192.168.1.0/24 -o enp0s8 -j MASQUERADE')
    net.get('r0').cmd('iptables -P FORWARD ACCEPT')

    net.get('r1').cmd('sysctl -w net.ipv4.ip_forward=1')
    net.get('r1').cmd('iptables -P FORWARD ACCEPT')


def run():
    topo = NetworkTopo()
    net = Mininet( topo=topo, switch=None, controller=None )
    config(net)
    net.start()
    info( '*** Done (network started).\n' )
    CLI( net )
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    run()
