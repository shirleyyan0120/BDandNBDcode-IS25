
# AAD_4direction_code

## Guidance

1. **Download Raw Data**
   - Download the raw data from [Zenodo](https://zenodo.org/records/14887886) and copy it to the `rawdata` directory.

2. **Preprocess**
   - Preprocess the EEG data.

3. **Analysis**
   - Run matlab and python codes to analysis.
    

## File Structure

### scalp-eeg

#### analysis

- **matlab**
  - **code_env**
    - `envelope_process_neu`: The code for "3.2. Stimulus reconstruction".
  - **code_space**
    - `preprocess_IIR`: Preprocess data to prepare for ASAD.
    - `mak.py`: Generate pseudo-labels and save them to the target path.

- **python**
  - **EEG_code**
    - `main.py`: The code to run the results in Table 1 and Table 2.

#### preprocess

- `cuteeg.m`: Cut the processed data from raw EEG data as described in section 2.3.

#### preprocess_data

- *No files currently*: Data will be available after running `cuteeg.m`.

#### rawdata

- *No files currently*: The raw data was released. Please download raw data from [Zenodo](https://zenodo.org/records/14887886).

#### Scalp_ITPC

- `CALITPC.m`: The code for section 4.1 "ITPC".


### ear-eeg

#### analysis

- **matlab**
  - **code_env**
    - `envelope_process_ear`: The code for "3.2. Stimulus reconstruction".
  - **code_space**
    - `preprocess_IIR`: Preprocess data to prepare for ASAD.
    - `mak.py`: Generate pseudo-labels and save them to the target path.

- **python**
  - **EAR_code**
    - `main.py`: The code to run the results in Table 1 and Table 2.

#### preprocess

- `cuteeg.m`: Cut the processed data from raw ear-EEG data as described in section 2.3.

#### preprocess_data

- *No files currently*: Data will be available after running `cuteeg.m`.

#### rawdata

- *No files currently*: The raw data was released. Please download raw data from [Zenodo](https://zenodo.org/records/14887886).

#### Ear_ITPC

- `CALITPC.m`: The code for section 4.1 "ITPC".

