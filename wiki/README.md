# AXIOM Infinite Wiki

A zero-dependency browser encyclopedia that streams concise topic definitions from the Gemini API and turns generated words into navigable topics.

## Properties

- Single-file application: HTML, CSS, and JavaScript live in `index.html`.
- No build step, package manager, SDK, framework, or runtime dependency.
- Native SSE streaming with cancellation of superseded requests.
- Gemini API keys are held only in page memory and sent in the `x-goog-api-key` request header.
- Generated content is inserted as text, not trusted HTML.
- A restrictive Content Security Policy limits network access to Google's Gemini API.
- Keyboard-accessible generated topic links and responsive controls.

## Usage

Open `index.html` in a modern browser, enter a Gemini API key, then search or select `rand`. Generated words can be clicked to traverse to another topic.

The configured model is `gemini-3.5-flash-lite`. API availability, quotas, and charges are controlled by the Google account associated with the supplied key; this project does not enable billing or paid capacity.

## Security boundary

This is a client-side application. The API key is necessarily available to the browser page while in use. It is not persisted by the application and is not placed in the request URL, local storage, cookies, generated content, or repository state. Use a key whose restrictions and quota are appropriate for client-side use.

Model output is untrusted content. The application renders generated text through DOM text nodes and does not execute generated markup or commands.

## Validation

Run:

```bash
python3 -m unittest -v tests/test_browser.py
```

The test launches local headless Chromium against an instrumented copy of the page. Network requests are mocked; it covers streaming, request cancellation, generated-topic navigation, and HTTP error handling without consuming Gemini quota.

## License

MIT. See `LICENSE`.
