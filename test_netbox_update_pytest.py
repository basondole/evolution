""" Test modules """
import pytest
import netbox_update_os as nb


@pytest.fixture
def data():
    """Test data"""
    url = "https://master.netbox.dev/"
    token = "72598a1ecdcdd229c19b38ad736b23225cbeb71f"
    filter_id = 86
    ip_address = "192.168.56.36"
    user = "testuser"
    passwd = "testpass"
    driver = "ios"
    os_version = (
        "7200 Software (C7200-ADVENTERPRISEK9-M),"
        " Version 15.3(3)XB12, RELEASE SOFTWARE (fc2)"
    )

    return {
        "url": url,
        "token": token,
        "driver": nb.get_network_driver(driver),
        "ip_address": ip_address,
        "user": user,
        "passwd": passwd,
        "os_version": os_version,
        "device": nb.get_devices_from_netbox(
            url, token, id_filter=filter_id
        ).__next__(),
    }


def test_retrieved_driver():
    """
    Test the drivers ro be used with napalm.

    NOTE:
      PANOS requires napalm==2.5, while some other modules require napalm version 3+
      A modified napalm-panos module panos.py is included in this dir and should replace
      The stock panos.py in the napalm-panos installation directory.

      ALTENATIVELY comment out line 52 in this function and and skip testing for PANOS.

      DEFAULT: Line 52 will be commented out.
    """
    assert nb.get_napalm_driver("Cisco Catalyst IOS") is nb.get_network_driver("ios")
    assert nb.get_napalm_driver("Cisco Nexus OS") is nb.get_network_driver("nxos")
    assert nb.get_napalm_driver("Cisco ASA OS") is nb.get_network_driver("asa")
    assert nb.get_napalm_driver("Aruba OS") == nb.get_network_driver("aoscx")
    # assert nb.get_napalm_driver('PaloAlto PAN-OS') == nb.get_network_driver('panos')


def test_response_from_netbox(data):
    """Assert the data type response from netbox"""
    response = nb.get_devices_from_netbox(url=data["url"], token=data["token"])
    assert response is not None
    assert response.__class__.__name__ == "RecordSet"
    assert "sw_version" in response.__next__().custom_fields.keys()


def test_response_from_napalm(data):
    """Verify the os version from test device matches the expected"""
    assert (
        nb.get_os_version(
            data["driver"], data["ip_address"], data["user"], data["passwd"]
        )
        == data["os_version"]
    )


def test_update_netbox_record(data):
    """Asses by updating existing record with identical software version"""
    device = data["device"]
    existing_os_record = device.custom_fields["sw_version"]
    assert nb.update_os_version_record(device, existing_os_record) is False
    if existing_os_record != data["os_version"]:
        assert nb.update_os_version_record(device, data["os_version"]) is True
        # restore original record
        nb.update_os_version_record(device, existing_os_record)
