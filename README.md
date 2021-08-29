**IMPORTANT**

The stock panos module from `pip install napalm-panos` has issues running with napalm 
version 3+. The modified `panos.py` file included in this directory should be 
copied to the `napalm-panos` installation directory and replace the stock `panos.py`

**About**

This code collects software version information directly from the network devices (`Cisco Catalyst IOS`, `Cisco Nexus OS`, `Cisco ASA OS`, `Aruba OS`, `PaloAlto PAN-OS`), and updates custom field `sw_version` in Netbox for each device with `Status = Active`, `Tenant = NOC` in Netbox.

****NB:****
- The directory contains unit tests (pytest)
- The code file `netbox_update_os.py` passes `pylint` and `black`.
- The file `test_hosts.txt` contains virtual machines I used for unit testing.


***Installation***

`pip install -r requirements.txt`


***Unit testing***

`pytest -v test_netbox_update_pytest.py`

Variables can be copied from `test_hosts.txt` to the `data` function in `test_netbox_update_pytest.py` to simulate different test cases for different device models. 
