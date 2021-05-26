import PySimpleGUI as sg
from netmiko import Netmiko
from netmiko.ssh_exception import NetMikoAuthenticationException, NetMikoTimeoutException
import concurrent.futures as cf
import encodings.idna
import time
import os
import textfsm
import ntc_templates
import pprint

#menu_def = [['Select Vendor/Platform', ['cisco_ios', 'cisco_xr', 'cisco_asa', 'juniper', 'arista_eos']]]
sg.ChangeLookAndFeel('GreenTan')
with open('ip_list.txt', 'r') as ip_list:
    ips = ip_list.read().splitlines()

def config_change(ips):
    try:

        cisco_IOS = {
                'device_type': 'cisco_ios',
                'host': ips,
                'username': username,
                'password': password,
                'secret': password,
                'timeout': 10000,
                'session_timeout': 10000}
        net_connect = Netmiko(**cisco_IOS)
        net_connect.enable()
        with open('config_change.txt') as commands:
            command = commands.read().splitlines()

#        g_output = net_connect.send_config_from_file(config_file="config_change.txt")
            g_output = net_connect.send_config_set(command)
        net_connect.disconnect()
        return "-----------Working on host " + ips + " -----------\n" + g_output + "\n"
#    except ValueError:

    except NetMikoTimeoutException:
        w = open('status_output.txt', 'a')
        w.write("ERROR: connection to " + ips + " timed-out.")
        w.close()
    except NetMikoAuthenticationException:
        k = open('status_output.txt', 'a')
        k.write("ERROR: Authentication failed for " + ips)
        k.close()

def status_check(ips):
    try:

        cisco_IOS = {
                'device_type': 'cisco_ios',
                'host': ips,
                'username': username,
                'password': password,
                'secret': password,
                'timeout': 10000,
                'session_timeout': 10000}
        net_connect = Netmiko(**cisco_IOS)
        net_connect.enable()
        with open('status_check.txt') as command:
            output = ''
            for commands in command:
                output += "=====>" + commands + net_connect.send_command(commands) + '\n'
        net_connect.disconnect()
        return "-----> Working on host " + ips + " <-----" "\n" + output + "\n"
    except ValueError:
        pass
    except NetMikoTimeoutException:
        print("ERROR: connection to " + ips + " timed-out.\n")
    except NetMikoAuthenticationException:
        print("ERROR: Authentication failed for " + ips)


def backup(ips):

    try:
        cisco_IOS = {
                'device_type': 'cisco_ios',
                'host': ips,
                'username': username,
                'password': password,
                'secret': password,
                'timeout': 10000,
                'session_timeout': 10000}
        net_connect = Netmiko(**cisco_IOS)
        net_connect.enable()
        out = net_connect.send_command("show running-config")
        net_connect.disconnect()
        with open(path + '/' + ips + '.txt', 'w') as fileouts:
            fileouts.write(out)

    except ValueError:
        pass
    except NetMikoTimeoutException:
        print("ERROR: connection to " + ips + " timed-out.\n")
    except NetMikoAuthenticationException:
        print("ERROR: Authenticaftion failed for " + ips)
def save_config(ips):
    try:
        cisco_IOS = {
                'device_type': "cisco_ios",
                'host': ips,
                'username': username,
                'password': password,
                'secret': password,
                'timeout': 10000,
                'session_timeout': 10000}
        net_connect = Netmiko(**cisco_IOS)
        net_connect.enable()
        output = net_connect.send_command('wr mem')
        net_connect.disconnect()
        return output
    except ValueError:
        pass
    except NetMikoTimeoutException:
        print("ERROR: connection to " + ips + " timed-out.\n")
    except NetMikoAuthenticationException:
        print("ERROR: Authentication failed for " + ips)

layout = [[sg.Image(r'C:\Users\nzt39f\PycharmProjects\elshat_project\81aea525d23345b19b952b6df1963453.png')],
#    [sg.Menu(menu_def, tearoff=True)],
    [sg.Text('Network Automation', size=(25, 1), justification='center', text_color='White', font=("Helvetica", 25), relief=sg.RELIEF_RIDGE)],
          [sg.Text('SSH Login --'),sg.Text(' ' * 70, ), sg.Text("Select Vendor/Platform"), sg.InputOptionMenu(('cisco_ios', 'cisco_xr', 'cisco_asa', 'juniper', 'arista_eos'))],
          [sg.Text('Username'), sg.Input( size=(30, 1))],
      [sg.Text('Password'), sg.Input(size=(30, 1), password_char='*')],
    [sg.Text("Please select from below options: \n"
             "'1' -- Run status check \n"
             "'2' -- Run config change \n")],
    [sg.Input(size=(30, 1))],
    [sg.Button('Run'), sg.Text(' ' *70), sg.Button('Save the config change')],
    [sg.Text('_'  * 100)],
    [sg.Text('Configuration Backup', size=(35, 1))],
    [sg.Text("Backup To: "), sg.Input(key="-IN2-" ,change_submits=True), sg.FolderBrowse(key="-IN-")],[sg.Button("Submit")]]



window = sg.Window('Automate everything-Cisco platform', layout, default_element_size=(100, 50), grab_anywhere=False)
while True:  # The Event Loop
    event, values = window.read(timeout=5000)
    if event == sg.WIN_CLOSED:
        break

    if event == 'Run' and values[3] == '1':
        username = values[1]
        password = values[2]
        start = time.perf_counter()
        with cf.ThreadPoolExecutor(max_workers=500) as executor:
            result = executor.map(status_check, ips)
            f = open('status_output.txt', 'w')
            for results in result:
                f.write(str(results) + '\n')
            f.close()
        finish = time.perf_counter()
        d = open('status_output.txt', 'a')
        d.write('Finished in ' + str(round(finish - start, 2)) + 'second(s)')
        d.close()
        sg.popup('your task is done')
        window.refresh()
    if event == 'Run' and values[3] == '2':
        username = values[1]
        password = values[2]
        start = time.perf_counter()
        with cf.ThreadPoolExecutor(max_workers=500) as executor:
            result = executor.map(config_change, ips)
        sg.popup('your task is done')
        window.refresh()
    if event == 'Submit':
        username = values[1]
        password = values[2]
        path = values["-IN-"]
        start = time.perf_counter()
        with cf.ThreadPoolExecutor(max_workers=500) as executor:
            result = executor.map(backup, ips)
        finish = time.perf_counter()
        g = open(path + '/Speed.txt', 'w')
        g.write('Finished in ' + str(round(finish - start, 2)) + 'second(s)')
        g.close()
        sg.popup('your task is done')
        window.refresh()
    if event == 'Save the config change':
        username = values[1]
        password = values[2]
        with cf.ThreadPoolExecutor(max_workers=500) as executor:
            result = executor.map(save_config, ips)
        sg.popup('config saved!')
window.close()
