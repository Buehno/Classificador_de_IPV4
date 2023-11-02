from cx_Freeze import setup, Executable

executables = [Executable("IPV4-end.py")]

setup(
    name="OptiDrive-IP",
    version="1.0",
    description="Saiba suas predefinições ip e calcule ips alheios",
    executables=executables
)