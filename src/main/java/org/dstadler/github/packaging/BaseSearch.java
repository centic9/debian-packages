package org.dstadler.github.packaging;

import org.apache.commons.lang3.StringUtils;
import org.kohsuke.github.GitHub;
import org.kohsuke.github.GitHubBuilder;
import org.kohsuke.github.RateLimitChecker;
import org.kohsuke.github.RateLimitTarget;

import java.io.IOException;

/**
 * Base class for different code-searchers
 */
public abstract class BaseSearch {
    public static GitHub connect() throws IOException {
        GitHubBuilder builder = GitHubBuilder.fromEnvironment();

        // this can increase rate-limits considerably
        String token = System.getenv("GITHUB_TOKEN");
        if (StringUtils.isNotBlank(token)) {
            System.out.println("Using provided GITHUB_TOKEN");
            builder.withJwtToken(token);
        }

        return builder.
                // observe rate-limits and wait if we get near the returned remaining number of requests per timeframe
                withRateLimitChecker(new RateLimitChecker.LiteralValue(1), RateLimitTarget.SEARCH).
                build();
    }
}
