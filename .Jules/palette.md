## 2024-05-18 - Added Helpful Tooltips and Loading States to NREL API Form
**Learning:** In Streamlit apps with long-running external API calls, users often lack immediate feedback on action execution. Static `st.info` messages are insufficient. Additionally, input fields lacking explicit format descriptions can cause user errors, especially with complex formats like TMY years or decimal coordinates.
**Action:** When implementing Streamlit forms, always utilize `st.spinner()` for asynchronous or long-running tasks to provide visual loading feedback. Use the `help` parameter on `st.text_input` and `st.button` components to offer contextual guidance and tooltips without cluttering the UI. Promote primary actions using `type="primary"` on buttons.
## 2024-05-18 - Replacing Custom Base64 Download Links with Native Components
**Learning:** Custom HTML download links generated via Base64 encoding often lack the accessibility attributes (like `aria-label` or proper focus states) provided by native UI components, reducing usability for screen reader and keyboard-only users. Furthermore, they bypass framework-level optimizations and theming, resulting in inconsistent UI.
**Action:** Always prefer native framework features (e.g., Streamlit's `st.download_button`) over custom HTML string generation. Native components ensure consistent accessibility, better cross-browser compatibility, and seamless integration with the application's overall design system and behavior.
## 2024-05-18 - Replacing Text Inputs with Number Inputs for Coordinates
**Learning:** Using generic text inputs for numeric fields like latitude and longitude forces users to manually format data and increases the likelihood of invalid submissions (e.g. typos, out of bounds coordinates). This causes a poor user experience as errors might only be caught upon submission.
**Action:** When capturing numeric data, especially bounded data like coordinates, always prefer native `st.number_input`. Utilize `min_value`, `max_value`, and `format` arguments to proactively enforce constraints, provide up/down stepper controls, and guarantee cleanly formatted float inputs.
## 2024-05-20 - Suppressing Streamlit's Missing Secrets Warning
**Learning:** Accessing `st.secrets` directly when a `.streamlit/secrets.toml` file does not exist triggers an ugly, unavoidable pink error trace in the Streamlit UI, creating a jarring first impression for new users setting up the project locally.
**Action:** When retrieving optional API keys or configurations from Streamlit's secrets manager, proactively check for the existence of `secrets.toml` files (e.g., using `os.path.isfile()` for `./.streamlit/secrets.toml` and `~/.streamlit/secrets.toml`) before accessing `st.secrets` to gracefully handle unconfigured environments and maintain a clean user interface.

## 2026-03-12 - Using Dynamic Disabled States for Form Validation
**Learning:** In Streamlit applications, using `st.stop()` inside button click handlers for form validation provides a poor user experience. The button remains clickable even with invalid inputs, making the UI feel unresponsive when clicked, and the error is only shown after an action is attempted.
**Action:** Implement real-time inline validation by evaluating input states *before* the submit button is rendered. Use this evaluation state to dynamically set the button's `disabled` parameter and provide contextual validation feedback via the `help` parameter, ensuring a responsive and intuitive UI.

## 2024-06-15 - Pairing Map Interactions with Toast Feedback
**Learning:** Interactive widgets like maps (e.g., via `streamlit-folium`) update application state in the background upon interaction, but this state change is often invisible to the user until they scroll down to see updated input fields. This disconnect can cause confusion about whether the interaction was registered.
**Action:** When capturing input from complex interactive components like maps, immediately present a brief `st.toast` notification confirming the action (e.g., displaying the reverse-geocoded location name). Use `st.session_state` to track interaction IDs to prevent duplicate toasts across unrelated application reruns.

## 2024-06-18 - Inline Error Messages for Better Form Validation Feedback
**Learning:** In Streamlit applications, relying solely on tooltips over disabled buttons to communicate form validation errors hides crucial context from the user until they attempt to interact with the disabled element.
**Action:** Implement real-time inline validation feedback by evaluating input states *before* the submit button is rendered and displaying explicit error or warning messages directly adjacent to the relevant input fields using `st.error` or `st.warning`.

## 2026-03-15 - Dynamic Disabled States Need Explicit Inline Feedback
**Learning:** In Streamlit apps, relying solely on a button's `help` tooltip to explain *why* it is disabled (e.g., missing API key) is completely inaccessible to touch device users (mobile/tablet) and often missed by keyboard-only users.
**Action:** When a primary action button is disabled due to missing prerequisites, always provide an explicit, visible inline message (e.g., `st.warning` or `st.error`) near the button or the missing input field to ensure all users immediately understand the required action.

## 2026-03-20 - Responsive Sizing for Interactive Map Components
**Learning:** Hardcoding a fixed pixel width (e.g., `width=700`) for large interactive UI components like maps (e.g., `streamlit-folium`) causes significant usability issues on smaller screens (mobile/tablet) by introducing forced horizontal scrolling and breaking responsive layouts. Conversely, it wastes available screen real estate on larger desktop monitors.
**Action:** When integrating large interactive components in Streamlit apps, explicitly opt-in to fluid, responsive sizing by using `use_container_width=True` instead of specifying static pixel dimensions. This ensures the component gracefully adapts to all device sizes, significantly improving mobile accessibility and desktop presentation.

## 2024-05-18 - Inline Validation for Forms
**Learning:** Depending entirely on button disabled states or tooltip hints for form validation can leave users confused when fields are cleared, especially since tooltips are inaccessible on mobile devices.
**Action:** Always provide explicit, inline feedback right next to the corresponding input fields using tools like `st.error` before disabling form submission buttons.

## 2026-03-22 - Proactive Inline Validation for External Tokens
**Learning:** In Streamlit apps that connect to external APIs, only verifying inputs on submission (or worse, letting the backend handle invalid inputs and fail) leads to unnecessary network requests, delayed failure messages, and user frustration.
**Action:** When capturing well-structured credentials (like API keys) or strictly formatted strings, always implement proactive, inline validation based on expected attributes (e.g., string length or regex) *before* submission, providing immediate visual feedback right next to the relevant input field.

## 2024-05-22 - Visual Constraint Cues via Native Input Attributes
**Learning:** In Streamlit applications, requiring specific lengths for inputs like API keys without providing explicit UI constraints causes user frustration when copying/pasting malformed strings, relying on form validation that only triggers later.
**Action:** Always provide immediate visual constraints for required lengths. Utilizing `max_chars` on Streamlit `st.text_input` components implicitly restricts invalid inputs, and provides a clear character counter (e.g. `0/40`), acting as proactive inline validation without extra code.

## 2024-06-25 - Async Feedback for Cached API Calls Triggered by UI Interactions
**Learning:** Synchronous external API calls (like Nominatim reverse geocoding) triggered indirectly by UI interactions (like clicking a location on a map) can cause the app to hang silently for several seconds on cache misses, confusing users about whether their interaction was registered.
**Action:** When using `@st.cache_data` to memoize external API calls that are triggered by user interaction, explicitly opt-in to visual feedback by setting `show_spinner="Descriptive message..."`. This ensures the UI remains responsive and transparent during cache misses while preserving instant execution on cache hits.

## 2026-03-22 - Visual Constraints on Text Inputs Used for Filenames
**Learning:** In Streamlit applications, string inputs like "Location Name" that are eventually used to generate output filenames can cause confusion or errors if users input excessively long or malformed strings. While backend validation handles empty strings, unbounded text fields do not signal the expected input format visually.
**Action:** When capturing free-text input destined for filenames or external systems, consistently enforce sensible constraints using `max_chars` on `st.text_input()`. This immediately displays a character counter in the UI, gently guiding users and implicitly preventing egregiously long strings before submission, serving as proactive inline validation without needing extra custom code.

## 2024-06-26 - Dynamic API Key Labeling
**Learning:** In Streamlit apps with default credentials, labelling an override input as 'optional' can be misleading if no default key is actually configured or present, confusing users as to whether input is required.
**Action:** Dynamically update form labels and help text based on the presence of required configurations, indicating when an input is 'required' versus 'optional', providing a clearer user experience.

## 2024-07-10 - Explicit Browser Tab Titles and Icons via Page Config
**Learning:** By default, a Streamlit application displays a generic "Streamlit" label and logo in the browser tab. For users who work with many browser tabs open, this generic presentation makes the application hard to find and feels unpolished, negatively impacting the user experience and task efficiency.
**Action:** Always call `st.set_page_config` as the very first Streamlit command in the application's entry point to explicitly set a contextually relevant `page_title` and `page_icon`. This ensures the application is easily identifiable among other open browser tabs and presents a professional, cohesive brand experience.

## 2024-03-24 - Fine-Grained Stepping for Coordinate Inputs
**Learning:** By default, Streamlit assigns a step size of 0.01 to float `number_input` components unless specified otherwise. For geographic coordinates (latitude/longitude), 0.01 degrees represents a massive physical distance (~1.1 kilometers). This renders the native up/down stepper controls (and keyboard up/down arrows) practically useless for making fine location adjustments, forcing users to manually type out decimals.
**Action:** Always explicitly define a small, context-appropriate `step` value (e.g., `step=0.0001`, approx 11 meters) for numeric inputs representing GPS coordinates. This ensures the native UI stepper controls and keyboard arrows provide meaningful, fine-grained adjustments, improving accessibility and overall form usability.

## 2026-03-25 - Avoid "Click Here" Anti-Pattern for Links
**Learning:** Using non-descriptive link text like "here" or "click here" is an accessibility anti-pattern. Screen reader users often navigate by pulling up a list of all links on a page. In this context, "here" provides zero information about the link's destination or purpose, severely degrading the usability of the interface for visually impaired users.
**Action:** Always ensure link text is descriptive and clearly indicates the destination or action independently of the surrounding text. For example, instead of "To get an API key, click here", use "Please [request an NREL API key]".

## 2026-03-26 - Full-Width Action Buttons for Better Mobile UX
**Learning:** Default-sized primary action buttons (like "Submit" or "Download") in Streamlit applications often result in small touch targets, making them difficult to interact with on mobile devices and causing them to get visually lost underneath large form inputs on desktop views.
**Action:** Always use `use_container_width=True` on primary action buttons (like `st.button` and `st.download_button`) that complete a section or form. This explicitly increases the touch target size across all devices, significantly improving mobile usability and providing a clearer visual hierarchy at the end of a user flow.

## 2026-03-27 - Avoid Directional Language in Error and Info Messages
**Learning:** Using directional language like "above" or "below" in UI instructions or error messages is an accessibility anti-pattern (violating WCAG 1.3.3 Sensory Characteristics). Screen reader users navigate linearly, not spatially, and cannot perceive "above" or "below". Furthermore, visual layout changes in responsive designs can render directional instructions inaccurate.
**Action:** Always provide explicit, context-independent instructions. Instead of saying "Please provide an API key above", use descriptive references to the specific section or component, such as "Please provide an API key in the 'API Key Configuration' section".

## 2024-05-18 - Avoiding Exclusive Pointer-Driven Instructions for Interactive Widgets
**Learning:** Using instructions like "Click on the map..." is an accessibility anti-pattern (violates WCAG 1.3.3 Sensory Characteristics) because it assumes the user is using a pointer device (mouse, touch) and can see the widget. Screen reader users or keyboard-only users may interact with the interface differently (e.g. manually entering coordinates into inputs).
**Action:** When providing instructions for interactive graphical widgets like maps, avoid exclusive pointer-driven language. Use inclusive phrasing like "Select a location on the map, or enter coordinates manually" to accommodate all interaction modes and ensure instructions remain accurate for keyboard and assistive technology users.

## 2026-03-29 - Demystifying Domain Jargon and External Links with Inline Context
**Learning:** Users new to a specific domain (like building physics) often struggle with unexplained acronyms like "TMY" (Typical Meteorological Year). While tooltips offer hints, they are not mobile-friendly. Additionally, listing external tool links without descriptions forces users to click blindly to understand their value.
**Action:** Always provide unobtrusive inline explanations for domain-specific jargon (e.g., using `st.caption`) near the relevant input field. When providing links to external resources or tools, always append a brief description of what the tool does to set clear expectations and improve user confidence before clicking.

## 2024-05-18 - Replacing Markdown Headers with Info Callouts for External Tools
**Learning:** Stacking multiple plain `st.markdown` statements for supplementary information (like external tool links) after a primary success message can lead to visual fatigue and a poor hierarchy. Users might ignore the plain text, missing valuable resources. Using `st.info` as a visual callout significantly improves the prominence and grouping of these resources. However, it's critical to remember that `st.info` is not a layout container (like `st.container` or `st.expander`), but an element generator. Using it within a `with` block will cause subsequent elements to overwrite it, breaking the UI.
**Action:** When presenting supplementary but highly relevant information (like next steps or external tools), utilize `st.info` (or similar callouts) with an appropriate icon to create distinct visual groups. Always pass the content as a single, multi-line Markdown string directly to the `body` argument of `st.info`, and never attempt to use it as a `with` block container.

## 2026-04-01 - Inline File Previews for Confidence
**Learning:** Forcing users to download a plain-text/CSV file (like an EPW format file) without any visual confirmation of its contents forces them to switch contexts, open an external application, and disrupt their workflow just to verify the tool successfully generated the expected data.
**Action:** When offering text-based file downloads, use `st.expander` combined with `st.code` to provide a brief, inline preview of the file's contents (e.g., the first 10 lines) right before the download button. This allows users to quickly validate the data directly in the browser, increasing confidence and saving time before initiating the actual download.

## 2026-04-03 - Prevent Silent Fallbacks on Map Interactions and Improve Inline Help Accessibility
**Learning:** When interactive map widgets (like `streamlit-folium`) trigger reverse geocoding that fails (e.g., clicking on the ocean, which returns "Unknown Location"), silently falling back to a hardcoded default (like "Atlanta") creates misleading and inaccurate form data without the user realizing it. Additionally, hiding crucial form instructions (like "A descriptive name for the location, used to generate the output filename") inside a tooltip (`help` parameter) makes it completely inaccessible to mobile/touch device users, who cannot hover to reveal the text.
**Action:** When a secondary data fetch (like reverse geocoding) fails based on user input, explicitly clear the dependent form field to force the user to provide a manual fallback, rather than silently retaining a stale default value. Furthermore, always move critical field instructions out of tooltips and into explicit inline text (e.g., using `st.caption` directly beneath the input) to ensure full mobile accessibility and balanced visual layout.

## 2026-04-04 - Avoiding Inaccessible Tooltips
**Learning:** In Streamlit, instructions passed via the `help` parameter of input components are rendered as hover-only tooltips. These are completely inaccessible to users on mobile and touch devices, meaning critical context or formatting rules are hidden.
**Action:** Remove the `help` parameters and move critical instructions into explicit `st.caption` elements placed immediately below the inputs.
