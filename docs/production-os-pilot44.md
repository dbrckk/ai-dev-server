# Bounded source qualification 44

Pilot 43 failed before publishing source. Canary 40072166715 reported workflow
22d4f0f0520d48708130a312d7936b2a failed. Subsequent worker evidence recorded
provider quota failures and a blocked goal at 20 attempts. This remains a failure;
the sealed goal is not reset.

Main now includes provider routing correction #386 and capacity-yield correction
#392. Hosted diagnostic 40074183898 verified Lightning and Laguna responses,
a 192-token coding smoke, operator access and immediate worker-wake configuration.
This is readiness evidence, not proof of sustained provider capacity.

Sequence 44 creates one fresh bounded request for the still-applicable
production_os_latest_reviewer_state task. The existing 60,000-token ceiling,
provider configuration and exact assignment policy remain unchanged. No target
source edit is supplied locally. The model must produce the accepted edit, publish
its commit through the trusted handoff and obtain independent qualification on
that exact commit. Leave the resulting source PR draft and unmerged.

Success requires the worker and canary to report actual completion. Record source
SHA, PR, independent run and usage; a PR or local fixture alone is insufficient.
