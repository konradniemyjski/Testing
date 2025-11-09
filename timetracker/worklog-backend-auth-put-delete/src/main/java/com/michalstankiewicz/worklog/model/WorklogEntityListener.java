
package com.michalstankiewicz.worklog.model;

import jakarta.persistence.PrePersist;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;

public class WorklogEntityListener {
    @PrePersist
    public void setOwner(Worklog wl) {
        if (wl.getCreatedBy() == null || wl.getCreatedBy().isEmpty()) {
            Authentication auth = SecurityContextHolder.getContext().getAuthentication();
            if (auth != null) {
                wl.setCreatedBy(auth.getName());
            }
        }
    }
}
