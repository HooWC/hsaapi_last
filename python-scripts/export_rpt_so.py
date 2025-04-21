import sys
import win32com.client
import os

def export_report(so_id):
    try:
        print(f"Processing SO_ID: {so_id}")

        rpt_path = r"\\192.1.1.15\InfoApps\HSA\REPORTS\SALES\SO_ORIGINAL_SST.rpt"
        export_dir = r"\\192.1.1.15\InfoApps\HSA\REPORTS\SALES\pdf\SalesOrder"
        export_path = os.path.join(export_dir, f"SO_{so_id}.pdf")

        print(f"Report path: {rpt_path}")
        print(f"Export path: {export_path}")

        # Create export directory if it doesn't exist
        if not os.path.exists(export_dir):
            os.makedirs(export_dir)

        print("Initializing Crystal Reports...")
        cr_app = win32com.client.Dispatch("CrystalRuntime.Application.9")
        report = cr_app.OpenReport(rpt_path)
        print("Report loaded successfully")

        # Set up database connection
        print("Setting up database connection...")
        try:
            # Iterate through all tables and set connection info
            for i in range(1, report.Database.Tables.Count + 1):
                table = report.Database.Tables.Item(i)
                # Replace with actual database connection info
                table.SetLogonInfo("192.1.1.15", "InfoHSA", "", "hsonline")
                # Alternatively use more detailed connection properties
                # conn_info = table.ConnectionProperties
                # conn_info["User ID"] = "username"
                # conn_info["Password"] = "password"
                # conn_info["Data Source"] = "192.1.1.15"
                # conn_info["Initial Catalog"] = "InfoHSA"
            print("Database connection set up successfully")
        except Exception as e:
            print(f"Failed to set up database connection: {str(e)}")
            if hasattr(e, 'excepinfo') and e.excepinfo:
                print(f"COM error details: {e.excepinfo[2]}")
            return False

        # Set report parameters
        print("Setting report parameters...")
        param_name = "cso_id"
        try:
            param_field = report.ParameterFields.GetItemByName(param_name)
            param_field.ClearCurrentValueAndRange()
            param_field.AddCurrentValue(so_id)
            report.EnableParameterPrompting = False
            print(f"Parameters set successfully: {param_name} = {so_id}")
        except Exception as e:
            print(f"Failed to set parameters: {str(e)}")
            return False

        # Configure export options
        print("Configuring export options...")
        report.ExportOptions.FormatType = 31  # PDF format
        report.ExportOptions.DestinationType = 1  # Export to disk
        report.ExportOptions.DiskFileName = export_path

        # Execute export
        print("Exporting report...")
        try:
            report.Export(False)
            print(f"Export successful: {export_path}")
            return True
        except Exception as e:
            print(f"Export failed: {str(e)}")
            if hasattr(e, 'excepinfo') and e.excepinfo:
                print(f"COM error details: {e.excepinfo[2]}")
            return False

    except Exception as e:
        print(f"Unexpected error occurred: {str(e)}")
        return False

    finally:
        # Clean up objects
        if 'report' in locals():
            del report
        if 'cr_app' in locals():
            del cr_app

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python export_rpt.py <SO_ID>")
        sys.exit(1)

    so_id = sys.argv[1].strip().upper()
    if not so_id.startswith("SO"):
        print("Warning: SO_ID should start with 'SO'")
    
    if not export_report(so_id):
        sys.exit(1)  # Return non-zero status code for failure