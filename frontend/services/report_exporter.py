# Report exporter service for API Load Testing Dashboard frontend
import csv
from datetime import datetime
from collections import Counter

class ReportExporter:
    @staticmethod
    def export_to_csv(filepath: str, metrics: dict, details: list[dict]) -> bool:
        """
        Exports the individual request details of a test run to a CSV file.
        """
        try:
            with open(filepath, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Write Summary Information at the top
                writer.writerow(["API Load Testing Report"])
                writer.writerow(["Target URL", metrics["url"]])
                writer.writerow(["HTTP Method", metrics["method"]])
                writer.writerow(["Test Timestamp", metrics["timestamp"]])
                writer.writerow(["Total Requests", metrics["total_requests"]])
                writer.writerow(["Successful Requests", metrics["success_count"]])
                writer.writerow(["Failed Requests", metrics["failure_count"]])
                writer.writerow(["Average Response Time (s)", metrics["avg_response_time"]])
                writer.writerow(["Min Response Time (s)", metrics["min_response_time"]])
                writer.writerow(["Max Response Time (s)", metrics["max_response_time"]])
                writer.writerow(["Requests Per Second", metrics["requests_per_second"]])
                writer.writerow([]) # Empty spacer line
                
                # Write Headers for request details
                writer.writerow(["Request Index", "Status Code", "Response Time (s)", "Success", "Error Message"])
                
                # Write data rows
                for detail in details:
                    writer.writerow([
                        detail["request_index"],
                        detail.get("status_code", "N/A"),
                        round(detail["response_time"], 5),
                        1 if detail["success"] else 0,
                        detail.get("error_message") or ""
                    ])
            return True
        except Exception as e:
            print(f"Failed to export CSV: {e}")
            return False

    @staticmethod
    def export_to_text(filepath: str, metrics: dict, details: list[dict]) -> bool:
        """
        Exports a detailed textual analysis report of a test run.
        """
        try:
            # Aggregate status codes
            status_codes = [d.get("status_code") for d in details if d.get("status_code") is not None]
            code_counts = Counter(status_codes)
            
            # Aggregate errors
            errors = [d.get("error_message") for d in details if d.get("error_message") is not None]
            error_counts = Counter(errors)
            
            success_percentage = (metrics["success_count"] / metrics["total_requests"] * 100) if metrics["total_requests"] > 0 else 0
            
            report = []
            report.append("=" * 80)
            report.append("                     API LOAD TESTING REPORT - SUMMARY & ANALYSIS")
            report.append("=" * 80)
            report.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            report.append(f"Test Run Timestamp: {metrics['timestamp']}")
            report.append("-" * 80)
            report.append(f"Target URL:         {metrics['url']}")
            report.append(f"HTTP Method:        {metrics['method']}")
            report.append(f"Total Requests:     {metrics['total_requests']}")
            report.append("-" * 80)
            report.append("PERFORMANCE METRICS:")
            report.append(f"  - Success Rate:            {success_percentage:.2f}% ({metrics['success_count']} successful, {metrics['failure_count']} failed)")
            report.append(f"  - Average Response Time:   {metrics['avg_response_time']:.4f} seconds")
            report.append(f"  - Fastest Response:        {metrics['min_response_time']:.4f} seconds")
            report.append(f"  - Slowest Response:        {metrics['max_response_time']:.4f} seconds")
            report.append(f"  - Requests Per Second:     {metrics['requests_per_second']:.2f} RPS")
            report.append("-" * 80)
            
            report.append("STATUS CODE DISTRIBUTION:")
            for code, count in sorted(code_counts.items()):
                pct = (count / len(details) * 100) if len(details) > 0 else 0
                report.append(f"  - HTTP {code}: {count} occurrences ({pct:.1f}%)")
            report.append("-" * 80)
            
            if error_counts:
                report.append("ERROR LOG SUMMARY:")
                for err, count in sorted(error_counts.items(), key=lambda x: x[1], reverse=True):
                    pct = (count / len(details) * 100) if len(details) > 0 else 0
                    report.append(f"  - {err}: {count} occurrences ({pct:.1f}%)")
                report.append("-" * 80)
                
            report.append("DETAILED SAMPLE DATA (Top 20 requests):")
            report.append(f"  {'Index':<6} | {'Status':<6} | {'Time (s)':<10} | {'Result':<10}")
            report.append("  " + "-" * 40)
            for d in details[:20]:
                result_str = "SUCCESS" if d["success"] else "FAILED"
                report.append(f"  {d['request_index']:<6} | {str(d.get('status_code', 'N/A')):<6} | {d['response_time']:.4f}s    | {result_str:<10}")
            
            if len(details) > 20:
                report.append(f"  ... and {len(details) - 20} more requests (see CSV export for complete data).")
                
            report.append("=" * 80)
            
            with open(filepath, mode='w', encoding='utf-8') as f:
                f.write("\n".join(report))
            return True
        except Exception as e:
            print(f"Failed to export Text report: {e}")
            return False
