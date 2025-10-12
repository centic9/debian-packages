package org.dstadler.github.packaging;

import org.kohsuke.github.GHArtifact;
import org.kohsuke.github.GHRepository;
import org.kohsuke.github.GHWorkflow;
import org.kohsuke.github.GHWorkflowRun;
import org.kohsuke.github.GitHub;

import java.io.IOException;

/**
 * Lists all built artefacts in the GitHub Repository
 * at https://github.com/centic9/debian-packages/actions
 */
public class ListArtifacts {

    public static final String REPO_DEBIAN_PACKAGES = "centic9/debian-packages";

    // ID of GitHub Action "Build Debian Packages with Debcraft"
    public static final long WORKFLOW_ID = 177606114L;

    public static void main(String[] args) throws IOException {
        GitHub github = BaseSearch.connect();

        GHRepository repository = github.getRepository(REPO_DEBIAN_PACKAGES);
        for (GHWorkflow workflow : repository.listWorkflows()) {
            System.out.println("Workflow: " + workflow.getName() + ": " + workflow.getId());
        }

        for (GHWorkflowRun run : repository.getWorkflow(WORKFLOW_ID).listRuns()) {
            System.out.println("Run: " + run.getName() + ": " + run.getArtifactsUrl());

            for (GHArtifact artifact : run.listArtifacts()) {
                System.out.println("Artifact: " + artifact.getName());
            }
        }
    }
}
