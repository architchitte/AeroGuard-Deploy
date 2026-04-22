import joblib
import os
import sys

# Define absolute path to artifacts
BASE_DIR = r"c:\Users\MSUSERSL123\Desktop\New folder\AeroGuard-Deploy\AeroGuard-Backend\app\ml\artifacts"
SCALER_PATH = os.path.join(BASE_DIR, "scaler_y.joblib")

print(f"--- Artifact Integrity Check ---")
print(f"Target: {SCALER_PATH}")

if not os.path.exists(SCALER_PATH):
    print(f"ERROR: File not found. Please ensure scaler_y.joblib is in {BASE_DIR}")
    sys.exit(1)

try:
    scaler = joblib.load(SCALER_PATH)
    print(f"Object Type: {type(scaler)}")
    
    # Check for critical fitted attributes (StandardScaler has mean_, scale_; MinMaxScaler has scale_, min_)
    is_fitted = False
    attributes = ["scale_", "min_", "mean_", "n_features_in_"]
    
    found_attrs = []
    for attr in attributes:
        if hasattr(scaler, attr):
            found_attrs.append(attr)
            is_fitted = True
            
    if is_fitted:
        print(f"STATUS: SUCCESS")
        print(f"Fitted Attributes Found: {found_attrs}")
        # Print a snippet of the scale to be sure
        if hasattr(scaler, "scale_"):
            print(f"Scale Snippet: {scaler.scale_}")
            
        # Functional Test: Try inverse_transform
        try:
            import numpy as np
            # Create dummy data with correct number of features
            n_features = getattr(scaler, "n_features_in_", 1)
            dummy_data = np.zeros((1, n_features))
            result = scaler.inverse_transform(dummy_data)
            print(f"Functional Test SUCCESS: inverse_transform(zeros) = {result}")
        except Exception as e:
            print(f"Functional Test FAILURE: {e}")
    else:

        print(f"STATUS: FAILURE")
        print(f"Reason: Scaler object found but contains no fitted attributes. It appears to be an un-fitted instance.")
        
except Exception as e:
    print(f"STATUS: CRITICAL ERROR")
    print(f"Error Message: {e}")
