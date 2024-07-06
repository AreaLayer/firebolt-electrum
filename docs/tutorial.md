### Firebolt Electrum Mini Tutorial

#### Prerequisites

Before running the Firebolt-Electrum software, ensure you have the following:

- Python installed on your system. You can download it from the [official website](https://www.python.org/downloads/).
- Electrum set up in developer mode.
- A Testnet or Signet compatible setup for testing purposes.

#### Setting Up Firebolt Electrum

1. **Clone the Repository**

   First, clone the Firebolt-Electrum repository from GitHub to your local machine:

   ```sh
   git clone https://github.com/AreaLayer/firebolt-electrum.git
   cd firebolt-electrum
   ```

2. **Install Dependencies**

   Navigate to the project directory and install the necessary dependencies. Ensure you are using Python 3.7 or higher.

   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   pip install -r requirements.txt
   ```

3. **Configure Electrum**

   Ensure Electrum is set to developer mode. This can typically be done by running Electrum with the `--dev` flag. 

   ```sh
   electrum --dev
   ```

4. **Run Firebolt-Electrum**

   To start the firebolt-electrum application, use the provided script:

   ```sh
   ./run_electrum
   ```

#### Additional Configuration

- **Testnet/Signet Compatibility**: Ensure you are running Electrum on Testnet or Signet for testing. You can switch to Testnet or Signet by adding the `--testnet` or `--signet` flag when starting Electrum:

  ```sh
  electrum --testnet
  ```

  or

  ```sh
  electrum --signet
  ```

- **Developer Mode**: Make sure you are running Electrum in developer mode to enable all the necessary features for development and testing.

#### Verifying the Installation

After following the steps above, you should have Firebolt-Electrum up and running. You can verify the installation by checking the application output or by connecting to the Electrum console.

If you encounter any issues or need further assistance, refer to the [Firebolt-Electrum GitHub repository](https://github.com/AreaLayer/firebolt-electrum) for more detailed instructions and troubleshooting tips.

#### Contributing to Firebolt Electrum

If you wish to contribute to the project, follow these steps:

1. Fork the repository on GitHub.
2. Create a new branch for your feature or bugfix:

   ```sh
   git checkout -b my-new-feature
   ```

3. Make your changes and commit them:

   ```sh
   git commit -am 'Add new feature'
   ```

4. Push your branch to GitHub:

   ```sh
   git push origin my-new-feature
   ```

5. Create a pull request on GitHub, describing your changes in detail.

By following this mini-tutorial, you should be able to set up and run the Firebolt-Electrum project with ease. If you have any questions or need further assistance, feel free to ask!
