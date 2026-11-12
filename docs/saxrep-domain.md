# Connect SaxRep to saxrep.com

SaxRep uses the existing Hugo site and GitHub Pages deployment. The configured canonical URL is `https://saxrep.com/`. The repository remains `timrosenberg/SaxoBrain`, and the everyday Obsidian vault stays at `/Users/trosenberg/Documents/GitHub/SaxoBrain`.

## Current state

Checked on November 12, 2026, after Tim reported that Claude completed the domain setup:

- GitHub Pages reports the custom domain `saxrep.com` and the URL `http://saxrep.com/`.
- `saxrep.com` resolves to all four GitHub Pages A records listed below.
- `www.saxrep.com` has the CNAME target `timrosenberg.github.io`.
- `http://saxrep.com/` returns HTTP 200 from GitHub.
- HTTPS enforcement is disabled. The Pages API reports no certificate metadata, and an HTTPS request failed certificate hostname verification. HTTPS is not ready at this check.
- The older source configuration used `saxobrain.timothyrosenberg.com`. The Pages API does not report that hostname as its custom domain. Its historical use by visitors is unknown.

The Pages and DNS setup is in place. HTTPS readiness, HTTPS enforcement, and a successful publish using the new domain remain to verify. Source review and publication are tracked in [issue #6](https://github.com/timrosenberg/SaxoBrain/issues/6).

## Review and publish the rebrand

Review the change linked to [issue #6](https://github.com/timrosenberg/SaxoBrain/issues/6). Follow the structural review and merge process in [Publishing SaxRep](publishing.md). The agent needs Tim's explicit authorization before committing, pushing, merging, or publishing.

The workflow intentionally builds with the base URL returned by GitHub Pages. The source `baseURL` change is already included in this rebrand. It keeps local builds consistent with the intended HTTPS domain. It does not control the URL override used by the publishing workflow. Verify HTTPS readiness and the reported Pages URL before the next publish.

Keep the existing workflow concurrency group through the migration. This keeps deployment serialization consistent with already-running releases.

## Connect the domain

The Pages custom domain and DNS records below have already been configured. Keep these steps as the setup reference. Continue with HTTPS and release verification instead of repeating the completed settings changes.

1. Open the repository's [Pages settings](https://github.com/timrosenberg/SaxoBrain/settings/pages). Set the custom domain to `saxrep.com` and save it before changing DNS.
2. At the DNS provider, replace the root parking records with the following records. Remove a conflicting parking or forwarding record only as part of the approved domain cutover. Preserve unrelated mail, verification, and other service records.

   | Type | Host | Value |
   | --- | --- | --- |
   | A | @ | 185.199.108.153 |
   | A | @ | 185.199.109.153 |
   | A | @ | 185.199.110.153 |
   | A | @ | 185.199.111.153 |
   | CNAME | www | timrosenberg.github.io |

3. Wait for GitHub's domain check and HTTPS certificate to become ready. Check **Enforce HTTPS** when available. GitHub says DNS changes and HTTPS readiness can each take up to 24 hours.
4. After GitHub Pages reports `https://saxrep.com/`, run the normal **Publish site** workflow on `main` so generated canonical URLs, the sitemap, and redirect pages use the new domain.
5. Verify the release and links below before announcing the new address.

The `www` record points to `timrosenberg.github.io`, with no repository path. With `saxrep.com` selected as the custom domain and both records configured, GitHub Pages redirects `www.saxrep.com` to `saxrep.com`. The current publishing workflow obtains its domain from Pages settings; adding a source `CNAME` file is not the cutover mechanism for this workflow.

These records and setup steps follow GitHub's [custom-domain documentation](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site/managing-a-custom-domain-for-your-github-pages-site) and [HTTPS documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/securing-your-github-pages-site-with-https).

## Verify the live release

Read back the Pages settings and check DNS:

```sh
gh api repos/timrosenberg/SaxoBrain/pages --jq '{html_url,cname,https_enforced,build_type}'
dig +short saxrep.com A
dig +short www.saxrep.com CNAME
```

Confirm that `cname` is `saxrep.com`, the reported URL is `https://saxrep.com/`, and HTTPS is enforced. Confirm that the root DNS resolves to the four GitHub Pages addresses above.

Inspect the new domain at desktop and mobile widths. Check the catalog, one work, one composer, one album, a competition list, and a PDF page. Verify the SaxRep wordmark, page titles, and editorial headings. Test filters, navigation, media, and alias redirects. Check that canonical links and `sitemap.xml` use `https://saxrep.com/`.

Run the normal production smoke check against the verified artifact and its actual published revision. A local preview of uncommitted edits does not identify a published release.

Check incoming links from the previous GitHub address and the `www` variant. Do not announce either redirect as working until it is observed. Keep all permanent page slugs and existing aliases.

If `saxobrain.timothyrosenberg.com` has actually been shared, arrange and test a path-preserving redirect at its existing host. Changing the Pages custom-domain setting does not by itself establish a redirect service for a second custom hostname. Its current redirect status is unknown.

Update external links such as syllabi separately after the new address and relevant redirects pass these checks.

## Recovery

Before changing any live setting, record the Pages custom domain, HTTPS setting, and the DNS records being replaced. Keep this record until the new release and redirects are verified.

Recover published source changes through a checked revert PR under the normal publishing rules. If the new domain fails during cutover, restore the recorded Pages and DNS settings as needed and run **Publish site** on `main` so generated links match the restored host. Verify production against the resulting tested artifact. Preserve the existing slugs and aliases throughout recovery.
