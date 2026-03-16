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
