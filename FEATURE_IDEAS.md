# Feature Ideation: The Turtle-Themed Social App

This document captures brainstormed feature ideas that align with the core theme of the application: **turtle, chill, pixel art, and cute elements.** The goal is to create features that are not just skinned with the theme, but are *mechanically* aligned with it, promoting a calm, deliberate, and safe user experience.

---

### Idea 1: "The Shell" - A Private, Cozy Space

*   **Concept:** Every user gets a "Shell." This isn't their public profile; it's a private, non-performative space. Think of it as a digital journal or a cozy room. It's a direct counterpoint to the public-facing profile.
*   **Why it's "Turtle-like":** It embodies the idea of retreating into a safe, personal space. It's slow, reflective, and protected.
*   **Implementation Plan:**
    *   **v1 (Simple):** Create a new `ShellPost` model, linked one-to-one with a `Profile`. These posts are *only* visible to the user who created them. The UI for this would be a separate, calming, minimalist page—perhaps with a pixel art turtle in the corner.
    *   **v2 (Interactive):** The Shell could have a "Visitor's Log." You can't "like" a Shell, but you can leave a small, anonymous, pre-defined "gift" (e.g., a pixel art flower, a smooth stone). This encourages gentle, non-demanding interaction.

---

### Idea 2: "Incubating Posts" - The Slow Reveal

*   **Concept:** When you make a post, you can choose to have it "incubate." It won't appear on anyone's feed for a set period (e.g., 1 hour, 1 day). The user who posted it can see it, but for everyone else, it's a mystery.
*   **Why it's "Turtle-like":** It encourages deliberate thought and patience, like a turtle taking its time. It fights against the instant-gratification loop of other platforms.
*   **Implementation Plan:**
    *   **v1 (Core Logic):** Add a `publish_at` `DateTimeField` to the `Post` model. When a user creates a post, they can set this field. The main feed query would then filter for `publish_at <= now()`.
    *   **v2 (UI/UX):** On the feed, an incubating post could be represented as a cute, pixel-art "turtle egg." Clicking it might show a countdown timer. This creates gentle anticipation and a unique visual element for our feed.

---

### Idea 3: "The Journey" - Collaborative, Long-Form Posts

*   **Concept:** Instead of just individual posts, users can start a "Journey." A Journey is a slow-growing, collaborative story or collection. One person starts it with a picture and a sentence. Then, they can invite *one* friend to add the next piece. That friend adds their piece, and then they invite the next person, and so on.
*   **Why it's "Turtle-like":** It's about a long, steady journey, not a short sprint. It's collaborative and encourages thoughtful contribution over time.
*   **Implementation Plan:**
    *   **Models:** This is more complex. We'd need a `Journey` model and a `JourneyStep` model. Each `JourneyStep` would have a foreign key to the `Journey`, the `Profile` who created it, and the content (text/media). We'd also need a field to track whose "turn" it is.
    *   **UI/UX:** Visually, this could be stunning. Imagine a horizontal, scrolling timeline of pixel art and text, showing the path of the Journey. It becomes a beautiful, co-created artifact.
