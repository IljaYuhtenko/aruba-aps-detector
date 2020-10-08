# aruba-aps-detector
This script pulls data from Aruba controller to provide more information about specified APs

# Required files

1. List of APs that we're looking for, provided in arubs.csv file with the following syntax:

```
00000XXX;AL0000000
00000YYY;AL1111111
00000ZZZ;AL2387463
```

Where the first number is inventory number and the second one is the serial number of the AP

2. Parameters of the controller and group, provided in params.yml file with the following syntax:

```
group: example
controller: 10.10.10.1
```

The parameter name is self-explanatory

# Usage

After providing required data launch main.py, enter credentials, user and password.  
After the script has finished, you'll get file 'found.csv', which, in case of success, will include

```
00000ZZZ;AL2387463;d8:c7:c8:de:ad:bf;ap-name-01
```

It includes previously specified inventory and serial numbers, mac address of AP and it's name

