from prometheus_api_client import PrometheusConnect
import datetime
import os
import sys

# --- Configuration ---
PROMETHEUS_URL = os.getenv("PROMETHEUS_URL", "https://your-openshift-prometheus-route/api/v1")
PROMETHEUS_TOKEN = os.getenv("PROMETHEUS_TOKEN")

def get_single_promql_value(prom, promql_query):
    """
    Queries data using a custom PromQL query designed to return a single, latest value.
    """
    print(f"\n--- Executing Single-Value PromQL Query: '{promql_query}' ---", file=sys.stderr)

    try:
        result = prom.custom_query(query=promql_query)

        if not result:
            print(f"No data found for the query: '{promql_query}'.", file=sys.stderr)
            return None

        for series in result:
            metric_labels = series.get('metric', {})
            value_timestamp, value_str = series.get('value', [None, None])

            if value_timestamp is not None:
                dt_object = datetime.datetime.fromtimestamp(float(value_timestamp))
                print(f"Labels: {metric_labels}", file=sys.stderr)
                print(f"Value at {dt_object}: {float(value_str):.3f}", file=sys.stderr)
                return float(value_str)
            else:
                print("No value found in the result for this series.", file=sys.stderr)
                return None
        return None
    except Exception as e:
        print(f"Error executing single-value query for '{promql_query}': {e}", file=sys.stderr)
        return None


if __name__ == "__main__":
    if not PROMETHEUS_TOKEN:
        print("Error: PROMETHEUS_TOKEN environment variable not set.", file=sys.stderr)
        print("Please set it using: export PROMETHEUS_TOKEN=$(oc whoami -t)", file=sys.stderr)
        exit(1)

    headers = {
        "Authorization": f"Bearer {PROMETHEUS_TOKEN}"
    }

    try:
        prom = PrometheusConnect(url=PROMETHEUS_URL, headers=headers, disable_ssl=True)
        print(f"Successfully connected to Prometheus at {PROMETHEUS_URL}", file=sys.stderr)

        target_namespace = os.getenv("TARGET_NAMESPACE", "pwr-mntrng-test")
        target_pod_name = os.getenv("TARGET_POD_NAME")
        target_container_name = os.getenv("TARGET_CONTAINER_NAME", "hello-go-app")

        if not target_pod_name:
            print("Error: TARGET_POD_NAME environment variable not set.", file=sys.stderr)
            exit(1)

        KEPLER_JOULES_METRIC = "kepler_container_package_joules_total"

        avg_power_query = (
            f"rate({KEPLER_JOULES_METRIC}{{"
            f"container_namespace='{target_namespace}', "
            f"pod_name='{target_pod_name}', "
            f"container_name='{target_container_name}'"
            f"}}[5m])"
        )

        print("\n--- Getting Average Power (Watts) for the last 5 minutes ---", file=sys.stderr)
        avg_watts = get_single_promql_value(prom, avg_power_query)
        if avg_watts is not None:
            print(f"AVG_WATTS: {avg_watts:.3f}")

        total_joules_query = (
            f"sum by (container_namespace, pod_name, container_name) ("
            f"delta({KEPLER_JOULES_METRIC}{{"
            f"container_namespace='{target_namespace}', "
            f"pod_name='{target_pod_name}', "
            f"container_name='{target_container_name}'"
            f"}}[5m])"
            f")"
        )

        print("\n--- Getting Total Energy Consumed (Joules) for the last 5 minutes ---", file=sys.stderr)
        total_joules = get_single_promql_value(prom, total_joules_query)
        if total_joules is not None:
            print(f"TOTAL_JOULES: {total_joules:.3f}")

    except Exception as e:
        print(f"Failed to connect or query: {e}", file=sys.stderr)
        print(f"Please ensure Prometheus is running, accessible at {PROMETHEUS_URL}, and your token is valid.", file=sys.stderr)