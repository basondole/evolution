"""Netbox and NAPALM modules"""
import pynetbox
from napalm import get_network_driver


def get_devices_from_netbox(url, token, id_filter=None):
    """Gets devices records from netbox"""
    netbox_api = pynetbox.api(
        url=url,
        token=token,
    )
    if not id_filter:
        devices = netbox_api.dcim.devices.all()
    else:
        devices = netbox_api.dcim.devices.filter(id=id_filter)
    return devices


def get_napalm_driver(platform):
    """Genarates napalm driver name from device plaform for device connectivity"""
    if platform.lower() == "cisco catalyst ios":
        driver = get_network_driver("ios")

    elif platform.lower() == "cisco nexus os":
        driver = get_network_driver("nxos")

    elif platform.lower() == "cisco asa os":
        driver = get_network_driver("asa")

    elif platform.lower() == "aruba os":
        driver = get_network_driver("aoscx")

    elif platform.lower() == "paloalto pan-os":
        driver = get_network_driver("panos")

    return driver


def get_os_version(driver, ip_address, user, passwd):
    """Uses napalm getter to collect device facts and filter os version"""
    device = driver(hostname=ip_address, username=user, password=passwd)
    device.open()
    facts = device.get_facts()
    device.close()
    os_version = facts["os_version"]
    return os_version


def update_os_version_record(device, os_version):
    """Updates netbox os_version record with software version from device"""
    result = False
    existing_os_record = device.custom_fields["sw_version"]
    if str(existing_os_record) == str(os_version):
        print(f"Identical OS version record exists {str(os_version)}, not updated.")
    else:
        result = device.update(
            {"custom_fields": {"sw_version": "{}".format(os_version)}}
        )
        if result is True:
            print(
                f"Version for {device.name} has been updated from "
                f"{existing_os_record} to {os_version}."
            )
        else:
            print(f"Version for {device.name} failed to be updated to {os_version}.")
    return result


def main():
    """Collects device records from Netbox and updates os version with data from devices"""
    # User to specify the netbox url, token, ssh username and password for device access
    sshuser = "testuser"
    sshpass = "testpass"
    url = "https://master.netbox.dev/"
    token = "72598a1ecdcdd229c19b38ad736b23225cbeb71f"

    devices = get_devices_from_netbox(url, token)

    for device in devices:
        if (
            str(device.status).lower() == "active"
            and str(device.tenant).lower() == "noc"
        ):
            platform = str(device.platform)
            ip_address_cidr = str(device.primary_ip)

            ip_address = ip_address_cidr.split("/", maxsplit=1)[0]
            os_version = None

            driver = get_napalm_driver(platform)

            os_version = get_os_version(driver, ip_address, sshuser, sshpass)

            update_os_version_record(device, os_version)


if __name__ == "__main__":
    main()
