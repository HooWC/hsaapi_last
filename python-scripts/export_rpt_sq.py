import sys
import win32com.client
import os

def export_report(quot_id):
    try:
        print(f"Processing QUOT_ID: {quot_id}")

        # Fix 1: Ensure correct report file path
        rpt_path = r"\\192.1.1.15\InfoApps\HSA\REPORTS\SALES\SQ_ORIGINAL_SST.RPT"  # Removed redundant .RPT
        export_dir = r"\\192.1.1.15\InfoApps\HSA\REPORTS\SALES\pdf\SalesQuote"
        
        # Fix 2: Consistent use of quot_id variable
        export_path = os.path.join(export_dir, f"SQ_{quot_id}.pdf")  

        print(f"Report path: {rpt_path}")
        print(f"Export path: {export_path}")

        # Fix 3: Enhanced directory creation error handling
        try:
            if not os.path.exists(export_dir):
                os.makedirs(export_dir)
                print(f"Directory created: {export_dir}")
        except Exception as e:
            print(f"Failed to create directory: {str(e)}")
            return False

        # Fix 4: Added file existence check
        if not os.path.exists(rpt_path):
            print(f"Report file not found: {rpt_path}")
            return False

        print("Initializing Crystal Reports...")
        try:
            cr_app = win32com.client.Dispatch("CrystalRuntime.Application.9")
            report = cr_app.OpenReport(rpt_path)
            print("Report loaded successfully")
        except Exception as e:
            print(f"Failed to load report: {str(e)}")
            if hasattr(e, 'excepinfo') and e.excepinfo:
                print(f"COM error details: {e.excepinfo[2]}")
            return False

        # Set up database connection
        print("Setting up database connection...")
        try:
            for i in range(1, report.Database.Tables.Count + 1):
                table = report.Database.Tables.Item(i)
                table.SetLogonInfo("192.1.1.15", "InfoHSA", "", "hsonline")
            print("Database connection established successfully")
        except Exception as e:
            print(f"Failed to set up database connection: {str(e)}")
            if hasattr(e, 'excepinfo') and e.excepinfo:
                print(f"COM error details: {e.excepinfo[2]}")
            return False

        # Set report parameters
        print("Setting report parameters...")
        param_name = "cSqo_Id"
        try:
            param_field = report.ParameterFields.GetItemByName(param_name)
            param_field.ClearCurrentValueAndRange()
            param_field.AddCurrentValue(quot_id)
            report.EnableParameterPrompting = False
            print(f"Parameters set successfully: {param_name} = {quot_id}")
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
            # Verify export success
            if os.path.exists(export_path):
                print(f"Export successful: {export_path}")
                return True
            else:
                print(f"Export completed but file not generated: {export_path}")
                return False
        except Exception as e:
            print(f"Export failed: {str(e)}")
            if hasattr(e, 'excepinfo') and e.excepinfo:
                print(f"COM error details: {e.excepinfo[2]}")
            return False

    except Exception as e:
        print(f"Unexpected error occurred: {str(e)}")
        return False

    finally:
        if 'report' in locals():
            del report
        if 'cr_app' in locals():
            del cr_app

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python export_rpt_sq.py <SQ_ID>")
        sys.exit(1)

    # Fix 5: Consistent variable naming
    quot_id = sys.argv[1].strip().upper()
    if not quot_id.startswith("SQ"):
        print("Warning: QUOT_ID should start with 'SQ'")
    
    if not export_report(quot_id):
        sys.exit(1)