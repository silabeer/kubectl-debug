# Test kubectl debug

### Запуск тестового контейнера

```bash
k run ephemeral-demo --image=slurm:target --restart=Never --labels="my=pod"
```

### Подчключение к контейнеру

```bash
kubectl debug -it ephemeral-demo --image=slurm:debug  --target=ephemeral-demo
```

### Процессы в target контейнере
```bash
[root@ephemeral-demo /]# ps auxf
USER         PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND
root           7  0.0  0.0  11844  3044 pts/0    Ss   11:01   0:00 /bin/bash
root          29  0.0  0.0  51744  3480 pts/0    R+   11:04   0:00  \_ ps auxf
root           1  0.1  0.0  98352 19584 ?        Ss   10:59   0:00 /usr/bin/python3.9 -m http.server 8080
```
### Немного файловой системы
```bash
[root@ephemeral-demo /]# ls /proc/$(pgrep python)/root/usr/bin/python3.9
/proc/1/root/usr/bin/python3.9
```

### Tcdump в target
Запускаем локально
```bash
kubectl port-forward pod/ephemeral-demo 8080:8080
curl localhost:8080

```
Перехватываем трафик в контейнере

``` bash
[root@ephemeral-demo /]# tcpdump -i lo -n port 8080
tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
listening on lo, link-type EN10MB (Ethernet), capture size 262144 bytes
11:11:33.613152 IP 127.0.0.1.42266 > 127.0.0.1.webcache: Flags [S], seq 2580796693, win 65495, options [mss 65495,sackOK,TS val 603792058 ecr 0,nop,wscale 7], length 0
11:11:33.613163 IP 127.0.0.1.webcache > 127.0.0.1.42266: Flags [S.], seq 3774223132, ack 2580796694, win 65483, options [mss 65495,sackOK,TS val 603792058 ecr 603792058,nop,wscale 7], length 0
11:11:33.613172 IP 127.0.0.1.42266 > 127.0.0.1.webcache: Flags [.], ack 1, win 512, options [nop,nop,TS val 603792058 ecr 603792058], length 0
11:11:33.626562 IP 127.0.0.1.42266 > 127.0.0.1.webcache: Flags [P.], seq 1:78, ack 1, win 512, options [nop,nop,TS val 603792071 ecr 603792058], length 77: HTTP: GET / HTTP/1.1
11:11:33.626587 IP 127.0.0.1.webcache > 127.0.0.1.42266: Flags [.], ack 78, win 511, options [nop,nop,TS val 603792071 ecr 603792071], length 0
```
### Деплоим тестоый nginx

```
kubectl apply -f nginx.yml
```

Проверяем доступ из пода

```bash
[root@ephemeral-demo /]# curl 10.233.54.3
<!DOCTYPE html>
<html>
<head>
<title>Welcome to nginx!</title>
<style>
html { color-scheme: light dark; }
body { width: 35em; margin: 0 auto;
font-family: Tahoma, Verdana, Arial, sans-serif; }
</style>
</head>
<body>
<h1>Welcome to nginx!</h1>
<p>If you see this page, the nginx web server is successfully installed and
working. Further configuration is required.</p>

<p>For online documentation and support please refer to
<a href="http://nginx.org/">nginx.org</a>.<br/>
Commercial support is available at
<a href="http://nginx.com/">nginx.com</a>.</p>

<p><em>Thank you for using nginx.</em></p>
</body>
</html>
[root@ephemeral-demo /]#
```

Докидываем сетевые политики:
```
kubectl apply -f policy.yml
```
Проверяем доступ:

```bash
[root@ephemeral-demo /]# curl -v my-nginx
* About to connect() to my-nginx port 80 (#0)
*   Trying 10.233.54.3...
```

### Debug node
```bash
kubectl debug node/docker-desktop -it --image=slurm:debug
```
