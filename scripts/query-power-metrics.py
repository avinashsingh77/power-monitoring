from prometheus_api_client import PrometheusConnect
import datetime
import os

# --- Configuration ---
PROMETHEUS_URL = os.getenv("PROMETHEUS_URL", "https://your-openshift-prometheus-route/api/v1")
PROMETHEUS_TOKEN = os.getenv("PROMETHEUS_TOKEN")

def get_single_promql_value(prom, promql_query):
    """
    Queries data using a custom PromQL query designed to return a single, latest value.
    """
    print(f"\n--- Executing Single-Value PromQL Query: '{promql_query}' ---")

    try:
        result = prom.custom_query(query=promql_query)

        if not result:
            print(f"No data found for the query: '{promql_query}'.")
            return None

        # The result for a single value query will typically be a list of dicts.
        # Each dict contains 'metric' (labels) and 'value' ([timestamp, value]).
        # We usually expect only one series back for such an aggregated query.
        for series in result:
            metric_labels = series.get('metric', {})
            value_timestamp, value_str = series.get('value', [None, None])

            if value_timestamp is not None:
                dt_object = datetime.datetime.fromtimestamp(float(value_timestamp))
                print(f"Labels: {metric_labels}")
                print(f"Value at {dt_object}: {float(value_str):.3f}")
                return float(value_str)
            else:
                print("No value found in the result for this series.")
                return None
        return None
    except Exception as e:
        print(f"Error executing single-value query for '{promql_query}': {e}")
        return None


if __name__ == "__main__":
    if not PROMETHEUS_TOKEN:
        print("Error: PROMETHEUS_TOKEN environment variable not set.")
        print("Please set it using: export PROMETHEUS_TOKEN=$(oc whoami -t)")
        exit(1)

    headers = {
        "Authorization": f"Bearer {PROMETHEUS_TOKEN}"
    }

    try:
        prom = PrometheusConnect(url="https://"+PROMETHEUS_URL, headers=headers, disable_ssl=True)
        print(f"Successfully connected to Prometheus at {PROMETHEUS_URL}")

        # --- Define your container/pod details ---
        target_namespace = os.getenv("TARGET_NAMESPACE", "pwr-mntrng-test") # Use the values from your error message
        target_pod_name = os.getenv("TARGET_POD_NAME")
        target_container_name = os.getenv("TARGET_CONTAINER_NAME", "hello-go-app")

        if not target_pod_name:
            print("Error: TARGET_POD_NAME environment variable not set.")
            exit(1)

        KEPLER_JOULES_METRIC = "kepler_container_package_joules_total"

        # --- Option 1: Average Power (Watts) over the last 5 minutes ---
        # THIS IS THE CORRECTED QUERY.
        # It calculates the average rate of energy consumption (power)
        # for the specified container over the last 5 minutes.
        avg_power_query = (
            f"rate({KEPLER_JOULES_METRIC}{{"
            f"container_namespace=\"{target_namespace}\", "
            f"pod_name=\"{target_pod_name}\", "
            f"container_name=\"{target_container_name}\""
            f"}}[5m])" # The [5m] range selector goes INSIDE the rate() function
        )

        print("\n--- Getting Average Power (Watts) for the last 5 minutes ---")
        avg_watts = get_single_promql_value(prom, avg_power_query)
        if avg_watts is not None:
            print(f"Average Power for {target_pod_name}/{target_container_name} in last 5 min: {avg_watts:.3f} W")


        # --- Option 2: Total Energy Consumed (Joules) over the last 5 minutes ---
        # This remains the same as it was already correct.
        total_joules_query = (
            f"sum by (container_namespace, pod_name, container_name) ("
            f"delta({KEPLER_JOULES_METRIC}{{"
            f"container_namespace=\"{target_namespace}\", "
            f"pod_name=\"{target_pod_name}\", "
            f"container_name=\"{target_container_name}\""
            f"}}[5m])"
            f")"
        )

        print("\n--- Getting Total Energy Consumed (Joules) for the last 5 minutes ---")
        total_joules = get_single_promql_value(prom, total_joules_query)
        if total_joules is not None:
            print(f"Total Energy Consumed for {target_pod_name}/{target_container_name} in last 5 min: {total_joules:.3f} Joules")
            total_kwh = total_joules / 3.6e+6
            print(f"Which is equivalent to: {total_kwh:.6f} kWh")


    except Exception as e:
        print(f"Failed to connect or query: {e}")
        print(f"Please ensure Prometheus is running, accessible at {PROMETHEUS_URL}, and your token is valid.")