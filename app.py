from flask import Flask, render_template, redirect, request, url_for, send_from_directory
import requests
import os
import _thread
import time
from datetime import timedelta

app = Flask(__name__)
###init###
file_symbol = '/'
server_name = 'Starx Edge CDN Storage'
server_hello = 'Hi,Starx Server!'
main_url = 'https://www.ioflow.xyz'
main_protocol = 'HTTPS'
main_check_point = '/'
cdn_host_bound = 'cdn3.ioflow.xyz'
cdn_protocol = 'HTTPS'
cdn_check_point = '/'
##########
total_request = 0
total_forward = 0
total_error = 0
total_access_denies = 0
last_conn_check_time = 0
last_conn_status_ok = False
last_size_check_size = 0
##########
start_time = time.time()
##########
p_dir = os.getcwd()
static_dir = p_dir + file_symbol + 'static'


##########
def check_connection(url=main_url, point=main_check_point):
    global last_conn_check_time, last_conn_status_ok
    if last_conn_check_time == 0:
        last_conn_check_time = time.time()
    else:
        now_conn_check_time = time.time()
        # trigger as secs.
        if now_conn_check_time - last_conn_check_time <= 1800:
            print('Entering status cache.')
            print('Last_timestamp:', last_conn_check_time, 'Now_timestamp:', now_conn_check_time)
            if last_conn_status_ok:
                return 'OK'
            else:
                return 'Failed'
        else:
            last_conn_check_time = time.time()
    print('Getting Connection Status.')
    try:
        if requests.get(main_url + main_check_point).status_code == 200:
            last_conn_status_ok = True
            return 'OK'
        else:
            last_conn_status_ok = False
            return 'Failed'
    except Exception as e:
        print('Exception when checking {} connection:'.format(url), e)
        return False


def get_static_files_size():
    global last_size_check_size, last_conn_check_time
    if time.time() - last_conn_check_time < 3600:
        if last_size_check_size != 0:
            return last_size_check_size
    print('Getting Static Files size.')
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(static_dir):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    return str(total_size / 1048576)


def get_uptime():
    global start_time
    return timedelta(seconds=time.time() - start_time)


def forward_file(path):
    path_str = static_dir + path
    print('File dest:', path_str)
    if os.path.exists(path_str):
        if os.path.isfile(path_str):
            return True
        else:
            print('ERROR:', 'File dest is a folder!')
            return False
    print('Going to download function.')
    _thread.start_new_thread(download_file, (path, path_str))
    return False


def download_file(path, file_dest):
    global total_error
    f_dir = os.path.dirname(file_dest)
    if not os.path.exists(f_dir):
        os.makedirs(f_dir)
    s_url = main_url + path
    print('Dest URL:', s_url)
    with requests.get(s_url, stream=True) as r:
        try:
            r.raise_for_status()
        except Exception as e:
            total_error += 1
            print('ERROR AT DOWNLOADING:', s_url)
            print(e)
            return False
        with open(file_dest, 'wb') as f:
            print('Writing Binary:', file_dest)
            f.write(r.content)
            print('File download success:', file_dest)


@app.before_request
def upup():
    global total_request
    total_request += 1


@app.route('/')
def hello_world():
    return server_hello


@app.route('/index')
def root():
    return redirect('/')


@app.route('/info')
def info():
    # load target system is linux.
    return render_template('info.html', server_name=server_name, cilent_ip=request.access_route[-1],
                           c_status=check_connection(), c_l_time=time.ctime(last_conn_check_time),
                           s_l_avg=os.getloadavg()
                           , s_f_size=get_static_files_size() + ' MB', t_request=total_request, t_forward=total_forward,
                           t_error=total_error, t_denies=total_access_denies, c_time=get_uptime())


@app.errorhandler(404)
def resource_not_found(e):
    global total_forward, total_access_denies
    file_dest = request.path
    if not (file_dest.endswith('/') or len(os.path.basename(file_dest).split('.'))) < 2:
        if forward_file(file_dest):
            total_forward += 1
            local_dest = static_dir + os.path.dirname(file_dest)
            print('Forwarding:', local_dest)
            return send_from_directory(local_dest, os.path.basename(file_dest))
        else:
            print('File not stored:', file_dest)
            return redirect(main_url + file_dest)
    total_access_denies += 1
    return 'Access Denies.', 403


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, static_dir='static/')
