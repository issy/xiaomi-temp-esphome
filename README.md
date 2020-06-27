# What is this?

This is a script to generate a functional yaml section to flash an ESP32 with for Xiaomi BLE temperature sensors (gen 2)
This should be inserted at the bottom of your yaml and is generated from the `devices.txt` and `pairings.txt` files from the modified Xiaomi Home app by vevs found (here)[https://github.com/esphome/feature-requests/issues/552]

## How can I use this?

place the two files in the same directory as the script, run the script and it will produce a yaml file