cd scripts
until sudo python3 traceroute.py; do
    echo "Trace crash $?.  Respawning.. in 10 seconds" >&2
    sleep 10
done
cd ..