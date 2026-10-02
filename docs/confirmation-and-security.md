# Confirmation and takeover limits

PanicStick defaults to **Ask before each run**. In setup you may choose **Run without a start prompt** and select confirmations immediately before any chosen action. Declining a checkpoint stops the remaining actions. Earlier completed steps cannot be rolled back. Shutdown is always last; its checkpoint is selected by default when shutdown is configured, and can be removed deliberately in setup.

If someone or something has taken over the Mac, a prompt may be obscured, blocked, or manipulated. You may not be able to select Confirm. A prompt is not a security boundary against malware controlling your account. Unattended mode avoids waiting on the Mac UI, but means an unintended enabled trigger can start the sequence immediately. Test with notification-only first.

USB insertion triggers actions only if enabled in setup. The physical two-second button trigger can be configured independently.
