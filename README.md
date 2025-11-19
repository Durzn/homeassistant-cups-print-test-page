# CUPS Test Page Add-on for Home Assistant

This Home Assistant add-on provides a minimal interface to a remote CUPS server and exposes a single function: printing a test page. Its purpose is to keep inkjet printers from drying out by running a simple, periodic print.

The add-on is intentionally limited. It will not manage printers, modify CUPS settings, or provide general print services. It can be used to discover printers and print test pages for them.

## Features

- Connects to an existing CUPS server  
- Lists all configured printers  
- Provides an HTTP endpoint to trigger a test print  
- Intended for scheduled automation to prevent ink drying  
- Lightweight and minimal by design

## Configuration

In the add-on’s `config.json`, define:

```json
{
  "cups_host": "your-cups-server",
  "cups_port": 631
}
```

At runtime, Home Assistant provides these values to the container in:

```pgsql
/data/options.json
```

Example:

```json
{
  "cups_host": "192.168.1.50",
  "cups_port": 631
}
```

## API
`GET /printers`

Returns a list of printers available on the configured CUPS server.

`POST /print_test`

Prints a test page.

Payload:

```json
{
  "printer": "Printer_Name"
}
```

## Home Assistant Integration

### REST command

```yaml
rest_command:
  cups_print_test:
    url: "http://local-cups-print-test-page:5000/print_test"
    method: POST
    headers:
      Content-Type: application/json
    payload: '{"printer": "{{ printer }}"}'
```

**Note**: The URL that is needed to be used is specified here: https://developers.home-assistant.io/docs/add-ons/communication#network

### Lovelace Button
```yaml
type: button
name: Print Test Page
tap_action:
  action: call-service
  service: rest_command.cups_print_test
icon: mdi:printer
```