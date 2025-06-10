# Insight to CDS Publisher

A Python-based data integration tool that transfers time-series data from AVEVA Insight to AVEVA Data Services (formerly OSIsoft Cloud Services) using the OMF (OSIsoft Message Format) protocol.

## 🚀 Overview

This project provides a seamless way to:
- Extract historical and real-time data from AVEVA Insight
- Transform the data into OMF format
- Load the data into AVEVA Data Services for advanced analytics and visualization

The tool supports batch processing, multiple data types (Analog, Discrete, String), and handles large datasets efficiently with configurable batch sizes.

## 📋 Features

- **Multi-source Data Extraction**: Pull data from multiple AVEVA Insight sources simultaneously
- **Flexible Time Ranges**: Support for both absolute and relative time ranges
- **Data Type Support**: Handles Analog, Discrete, and String data types
- **Batch Processing**: Efficient handling of large datasets with configurable batch sizes
- **Error Handling**: Robust error handling and logging for production environments
- **Compression**: GZIP compression for data messages to optimize network usage
- **Authentication**: Secure OAuth2 authentication for both source and destination systems

## 🛠️ Prerequisites

- Python 3.8 or higher
- AVEVA Insight account with API access
- AVEVA Data Services account with appropriate permissions
- Required Python packages (see Installation section)

## 📦 Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Insight_To_CDS_Publisher.git
cd Insight_To_CDS_Publisher
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root with your credentials:
```env
# AVEVA Data Services Configuration
TenantId=your_tenant_id
NamespaceId=your_namespace_id
ClientId=your_client_id
ClientSecret=your_client_secret

# AVEVA Insight Configuration
USER_TOKEN_JARVIS=your_insight_user_token
```

## 📁 Project Structure

```
Insight_To_CDS_Publisher/
│
├── main/
│   ├── main.py                           # Main application entry point
│   ├── Start_main.bat                    # Windows batch file to run the application
│   └── _Insight_to_DataServices.ipynb    # Jupyter notebook for testing/development
│
├── src/
│   └── AvevaInsightLibrary.py           # AVEVA Insight API wrapper library
│
├── .env                                  # Environment variables (create this file)
├── requirements.txt                      # Python dependencies
└── README.md                            # This file
```

## 🚀 Usage

### Basic Usage

1. Configure your source tags in `main.py`:
```python
source_tagnames = [
    "PK-Sheikhupura.AOA.Pakistan.Sheikhupura.",
    "PH-Tanauan.AOA.Philippines.Tanauan.UTI01.AHR01.AH01."
]
```

2. Run the application:
```bash
python main/main.py
```

Or use the provided batch file on Windows:
```bash
main\Start_main.bat
```

### Advanced Configuration

#### Time Range Configuration
```python
# Use relative time (last 12 hours)
start_time = datetime.now() - timedelta(hours=12)
end_time = datetime.now()

# Or use absolute time
start_time = datetime(2024, 1, 1, 0, 0, 0)
end_time = datetime(2024, 1, 31, 23, 59, 59)
```

#### Batch Size Configuration
```python
# Adjust batch size for data processing (default: 5000)
process_and_send_data(data, streamName, batch_size=5000)
```

#### Data Retrieval Modes
```python
# Available retrieval modes: DELTA, INTERPOLATED, etc.
aveva.get_Insight_Data(tag, start_time, end_time, RetrievalMode="DELTA")
```

## 📊 Data Flow

1. **Authentication**: The application authenticates with both AVEVA Insight and Data Services
2. **Tag Discovery**: Retrieves available tags from specified source locations
3. **Type Definition**: Creates OMF type definitions in Data Services (if needed)
4. **Stream Creation**: Creates data streams for each tag
5. **Data Transfer**: Extracts data from Insight and sends to Data Services in batches
6. **Logging**: All operations are logged for monitoring and debugging

## 🔧 API Reference

### AvevaInsightLibrary

The main library provides the following key methods:

- `get_Tag_List(source_tagname)`: Retrieve list of tags from a source
- `get_Insight_Data(tag, start_time, end_time, RetrievalMode)`: Get historical data
- `check_tag_data_exists(tagname)`: Verify if a tag has recent data
- `get_Expression_Data(expression, start_time, end_time)`: Execute expressions

### OMF Integration

The application handles three OMF message types:
- **Type**: Defines the structure of data
- **Container**: Creates streams for data storage
- **Data**: Actual time-series data points

## 📝 Logging

The application uses Python's built-in logging module with the following format:
```
%(asctime)s - %(levelname)s - %(message)s
```

Log levels can be configured in `main.py`:
```python
logging.basicConfig(level=logging.INFO)  # Change to DEBUG for verbose output
```

## 🔒 Security Considerations

- Store sensitive credentials in environment variables
- Never commit `.env` files to version control
- Use secure connections (HTTPS) for all API calls
- Regularly rotate API keys and secrets
- Consider using Azure Key Vault or similar for production deployments

## 🐛 Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Verify all credentials in `.env` file
   - Check token expiration dates
   - Ensure proper permissions in both systems

2. **Connection Timeouts**
   - Check network connectivity
   - Verify firewall rules
   - Increase timeout values in API calls

3. **Data Type Mismatches**
   - Ensure OMF types match source data types
   - Check for null values in required fields

4. **Memory Issues with Large Datasets**
   - Reduce batch size
   - Process data in smaller time ranges
   - Monitor system resources

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- AVEVA for providing the Insight and Data Services platforms
- The Python community for excellent libraries
- Contributors and testers who help improve this tool

## 📞 Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Contact the development team
- Check the [Wiki](https://github.com/yourusername/Insight_To_CDS_Publisher/wiki) for detailed documentation

---

**Note**: This tool is not officially affiliated with or endorsed by AVEVA. Use at your own discretion and ensure compliance with your organization's data policies. 