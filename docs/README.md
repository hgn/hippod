
# Hippod - Problem Statement

Larger software projects often utilizes many different test systems. Each test
system/product comes with it own reporting tool making it difficult to get an
unified view across this heterogeneous landscape for specific software
versions. Hippod is a generic framework to unify the view in one common
application.

![alt text](images/hippod-test-system-interaction.png "Architecture")

# Installation

Hippod is written in Python3 using asyncio/aiohttp. To generate PDF reports
pandoc/xetex is required. For LDAP functionality libldap is required. Hippod
is tested on Debian/Ubuntu and Arch Linux. For Debian based systems the following
three lines should install all required dependencies:

```
sudo apt-get install python3-pip libsasl2-dev pandoc texlive-xetex
sudo apt-get install texlive-latex-extra texlive-latex-recommended libldap-dev
sudo pip3 install -r requirements.txt
```

To install hippod the next lines should do the trick:

```
# clone and install runtime files
git clone https://github.com/hgn/hippod.git
cd hippod
sudo make install

# edit configuration for LDAP support, if not defaults are fine
vim /etc/hippod/hippod-configuration.json

# start and enable hippod with systemd
sudo systemctl daemon-reload
sudo systemctl start hippod
sudo systemctl enable hippod

# follow logfile
sudo journalctl -f -u hippod
```

Point you webbrowser to localhost:8080 - that's all.

# Privacy Statement

Hippod will never query external resources like Java Script libraries or Google
Fonts. All resources are stored within hippod. Hippod can be operated behind
cooperate firewalls/proxies.


