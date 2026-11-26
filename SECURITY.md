# Security

## Reporting a vulnerability

Please do not report a security problem in a public issue, where anyone can read it before it is fixed.

Report it privately instead: on the [Security tab](https://github.com/mirkin-pixel/ha-unique-waterontharders/security) of this repository, choose **Report a vulnerability**. Only the maintainer sees the report. Say what is affected, how to reproduce it, and which version you run.

You get an answer within a week. Once a fix is out, the report is published with credit to you, unless you would rather stay unnamed.

## What is in scope

The integration as released here. The part worth a closer look is how it handles your API key, which it sends to the Unique Smart API and must never write to a log or a diagnostics file, and how it reads the data that API returns.

Problems in Home Assistant itself, in HACS, or in the Unique Smart API and the softener belong with those projects and with Unique.

## Supported versions

Fixes go into the latest release. There are no fixes for older versions: updating is the way to get one.
