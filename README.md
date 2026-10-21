# anvil-php

Static PHP builds for [Anvil](https://github.com/n1crack/anvil) on macOS and Linux.

Every day a workflow checks php.net for the newest release of PHP 8.1 to 8.5, and
php-src's tags for 8.6 previews (beta, RC). Each version not released here yet is built
from php.net's official source tarball (its SHA-256 checked against php.net) with
[static-php-cli](https://github.com/crazywhalecc/static-php-cli), pinned to one commit,
then smoke-tested and published as a release `php-<version>`.

## Files

Each release has, for `macos-aarch64`, `macos-x86_64`, `linux-x86_64` and `linux-aarch64`:

- `php-<version>-cli-<platform>.tar.gz`: the `php` binary
- `php-<version>-fpm-<platform>.tar.gz`: the `php-fpm` binary
- `SHA256SUMS`

The Linux builds are static (musl). The macOS builds need macOS 12 or later.

[`index.json`](index.json) lists the newest version of each minor, whether it is a
preview, and every file's URL and SHA-256:

    https://raw.githubusercontent.com/n1crack/anvil-php/main/index.json

## Extensions

Compiled in: bcmath, bz2, calendar, ctype, curl, dom, exif, fileinfo, filter, ftp, gd,
gmp, iconv, intl, mbregex, mbstring, mysqli, mysqlnd, opcache, openssl, pcntl, pdo,
pdo_mysql, pdo_pgsql, pdo_sqlite, pgsql, phar, posix, redis, session, simplexml, soap,
sockets, sodium, sqlite3, tokenizer, xml, xmlreader, xmlwriter, zip, zlib.

That is static-php's "common" set plus opcache, mysqli, intl and sodium.

PHP 8.6 previews take redis from phpredis' develop branch (pinned to a commit), since no
phpredis release builds against 8.6 yet.

## Smoke test

Before a release, each build must report its exact version in `php -v`, list every
extension above in `php -m`, and pass `php-fpm -t`. A version is released only when all
four platforms pass.
