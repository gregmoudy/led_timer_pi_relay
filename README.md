# led_timer_pi_relay
Holiday LED timer driven by a Raspberry Pi with a relay board on the GPIO.

To have this auto start in a terminal in the GUI of the Pi edit the following file.
sudo nano /etc/xdg/lxsession/LXDE-pi/autostart

And add this line to the end of it, save and reboot.
@lxterminal -e python /home/pi/led_timer_pi_relay/led_timer_pi_relay.py
