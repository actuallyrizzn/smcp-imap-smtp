# Malformed MIME Test Corpus

This directory contains intentionally malformed email samples for testing robust MIME parsing.

## Test Cases

### 1. Missing Boundary (`missing_boundary.eml`)
- Multipart message without boundary markers
- Tests parser's fallback behavior

### 2. Invalid Encoding (`invalid_encoding.eml`)
- Headers/body with invalid character encoding
- Tests UTF-8 error handling

### 3. Corrupted Headers (`corrupted_headers.eml`)
- Missing required headers (From, To, Date)
- Malformed header values
- Tests graceful degradation

### 4. Nested Multipart (`nested_multipart.eml`)
- Deeply nested multipart structures (5+ levels)
- Tests parser recursion limits

### 5. Missing Content-Type (`missing_content_type.eml`)
- Message without Content-Type header
- Tests default content type handling

### 6. Invalid Date Formats (`invalid_dates.eml`)
- Various invalid date header formats
- Tests date parsing fallbacks

### 7. Oversized Headers (`oversized_headers.eml`)
- Headers exceeding normal limits (10KB+)
- Tests header size limits

### 8. Mixed Encoding (`mixed_encoding.eml`)
- Messages mixing different character encodings
- Tests encoding detection and conversion

## Usage

These test files can be used to verify that the email parsing code handles malformed input gracefully without crashing.

## Generation

Test files are generated programmatically to ensure consistent test cases.

