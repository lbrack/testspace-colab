import os
import pathlib

# We use the configuration in the test directory - and avoid using the
# one from the user
config = pathlib.Path(__file__).parent / ".config" / "testspace" / "config"
os.environ["TS_COLAB_CONFIG"] = str(config)
print(f"setting test config {os.environ['TS_COLAB_CONFIG']}")
