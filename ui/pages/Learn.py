"""SafeClick Learn page: short awareness guides and checklists.

Educational content only. It describes warning signs and safe responses and
deliberately avoids operational detail that could be misused. SafeClick is an
awareness aid, not a security verdict, and the guides cover common patterns
only — scams are reworded constantly.
"""

from __future__ import annotations

import streamlit as st

st.set_page_config(
    page_title="Learn · SafeClick",
    page_icon=":material/menu_book:",
    layout="centered",
)

st.title(":material/menu_book: Learn to spot the patterns")
st.caption("Short, practical guides. A low risk score is never proof of safety.")

st.info(
    "Scams work by creating fear, urgency, or excitement so you act before you think. "
    "These guides help you slow down and check before you click, pay, or install.",
    icon=":material/school:",
)

phishing, digital_arrest, fake_apps, bad_urls, habits = st.tabs(
    ["Phishing", "Digital arrest", "Fake apps", "Suspicious URLs", "Good habits"]
)

with phishing:
    st.subheader("Phishing messages")
    st.markdown("Messages that imitate a trusted sender to get you to act fast.")
    st.markdown("**Warning signs**")
    st.markdown(
        "- [ ] Urgency or a deadline: “act now”, “within 24 hours”\n"
        "- [ ] A generic greeting instead of your name\n"
        "- [ ] A request for passwords, OTPs, card details, or KYC documents\n"
        "- [ ] A payment link or account number that does not match the organisation\n"
        "- [ ] A link whose address looks almost, but not exactly, right"
    )
    st.markdown("**Do this instead**")
    st.markdown(
        "- [ ] Do not reply, click, or download anything from the message\n"
        "- [ ] Contact the organisation using a number you look up yourself\n"
        "- [ ] Report and delete the message once you have checked"
    )
    st.caption("Common trick: a message says your account will be closed today unless you “verify” it.")

with digital_arrest:
    st.subheader("Digital arrest scams")
    st.markdown("A caller or message claims to be police, customs, or another agency and says you are under investigation.")
    st.markdown("**Warning signs**")
    st.markdown(
        "- [ ] A claim of a case, FIR, or warrant against you\n"
        "- [ ] Pressure to stay on the call and to tell no one\n"
        "- [ ] A demand for a “verification fee” or “clearance payment”\n"
        "- [ ] A request to join a video call to look “official”"
    )
    st.markdown("**Do this instead**")
    st.markdown(
        "- [ ] End the contact: real agencies do not collect payments over a call or message\n"
        "- [ ] Do not share Aadhaar, bank, card, or OTP details\n"
        "- [ ] Speak to someone you trust and report through an official channel"
    )
    st.caption("The name shown on caller ID can be faked, and a badge on a video call proves nothing.")

with fake_apps:
    st.subheader("Malicious app lures")
    st.markdown("Fake apps are spread through links, files, or “update” prompts.")
    st.markdown("**Warning signs**")
    st.markdown(
        "- [ ] A direct download link to an app file instead of an official store listing\n"
        "- [ ] Instructions to allow installs from unknown sources\n"
        "- [ ] Permissions unrelated to the app's purpose, such as reading SMS\n"
        "- [ ] An “update” that arrives by message or link"
    )
    st.markdown("**Do this instead**")
    st.markdown(
        "- [ ] Install apps only from the official store, and check the developer name\n"
        "- [ ] Ignore update prompts that arrive by message or link\n"
        "- [ ] Remove an app you installed by mistake and change important passwords"
    )
    st.caption("An app installed from outside the store can read your messages, steal OTPs, or lock your device.")

with bad_urls:
    st.subheader("Suspicious URLs")
    st.markdown("A link can look trustworthy and still lead somewhere harmful.")
    st.markdown("**Warning signs**")
    st.markdown(
        "- [ ] A domain that misspells or imitates a known brand\n"
        "- [ ] A very short link that hides the real destination\n"
        "- [ ] Odd characters or extra symbols inside the address\n"
        "- [ ] Long, confusing subdomains before the real domain\n"
        "- [ ] A sign-in page on a plain `http://` address"
    )
    st.markdown("**Do this instead**")
    st.markdown(
        "- [ ] Reach the site through the official app, or type the address yourself\n"
        "- [ ] Read the domain just before the first “/”, not the whole address\n"
        "- [ ] Prefer `https://`, but remember it alone does not prove a site is honest"
    )
    st.caption("SafeClick never opens a link for you. It only reads the address you paste.")

with habits:
    st.subheader("Good habits")
    st.markdown(
        "**Before you act**\n"
        "- [ ] Slow down: urgency is a tactic, not a reason to act\n"
        "- [ ] Verify through a channel you already trust, not one from the message\n"
        "- [ ] Never share OTPs, passwords, or card details to “confirm” anything\n"
        "- [ ] Tell someone you trust before paying or installing"
    )
    st.markdown("**If something already went wrong**")
    st.markdown(
        "- [ ] Stop contact and change the passwords you shared\n"
        "- [ ] Tell your bank and freeze the card if payment details leaked\n"
        "- [ ] Report it: in India call **1930** or use **cybercrime.gov.in**"
    )

st.divider()

st.subheader("Quick checklist before you act")
st.markdown(
    "- [ ] Is this asking me to act fast? If so, slow down.\n"
    "- [ ] Did I verify the sender through a channel I chose?\n"
    "- [ ] Am I being asked for an OTP, password, or a payment?\n"
    "- [ ] Have I told someone I trust?"
)

st.subheader("Limitations")
st.markdown(
    "- These guides cover common patterns; scams are reworded constantly.\n"
    "- A low SafeClick score is not proof that the content is safe.\n"
    "- SafeClick never opens links or files, so live page behaviour is not checked.\n"
    "- SafeClick is an educational aid, not professional security advice."
)

st.caption(
    "Educational tool · If you are a victim of fraud in India, call **1930** or report at **cybercrime.gov.in**."
)
