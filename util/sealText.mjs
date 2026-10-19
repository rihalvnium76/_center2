#!/usr/bin/env node
/**
 * sealText.mjs — 口令加密文件工具
 *
 * 用法:
 *   node sealText.mjs enc <输入文件> <输出文件>
 *   node sealText.mjs dec <输入文件> <输出文件>
 *
 * 口令来源:
 *   - 若环境变量 SEAL_PASS 非空，直接使用其值（不生成、不提示）
 *   - 否则 enc 从密码表随机生成并打印；dec 交互输入
 *
 * KDF:  PBKDF2-HMAC-SHA-256, salt 16B, 600000 迭代, 32B 密钥
 * AEAD: AES-256-GCM, nonce 12B, tag 16B, AAD 为空
 *
 * 容器自描述，包含解出明文所需的一切参数（无源码也能解）。
 */

import fs from 'node:fs';
import crypto from 'node:crypto';

// ─── 加密参数常量 ────────────────────────────────────────────────────────────
const KDF_NAME = 'PBKDF2-HMAC-SHA-256';
const KDF_ITER = 600_000;
const SALT_LEN = 16;
const KEY_LEN  = 32;

const CIPHER    = 'aes-256-gcm'; // 同时作为 Node 算法名与容器 alg 字段
const NONCE_LEN = 12;
const TAG_LEN   = 16;

// ─── 密码表与长度 ────────────────────────────────────────────────────────────
// 密码 = 从 CHARSET 中独立、等概率地随机抽取 LENGTH 个字符（可重复）。
const PASSWORD_CHARSET = '0123456789';
const PASSWORD_LENGTH  = 8;

const PASSWORD_DESC =
  `${PASSWORD_LENGTH} characters uniformly sampled with replacement ` +
  `from charset "${PASSWORD_CHARSET}"`;

// ─── 工具函数 ────────────────────────────────────────────────────────────────

/** 环境变量 SEAL_PASS 非空则返回其值，否则返回 null */
function passwordFromEnv() {
  const v = process.env.SEAL_PASS;
  return (typeof v === 'string' && v.length > 0) ? v : null;
}

function generatePassword() {
  const out = [];
  for (let i = 0; i < PASSWORD_LENGTH; i++) {
    out.push(PASSWORD_CHARSET[crypto.randomInt(0, PASSWORD_CHARSET.length)]);
  }
  return out.join('');
}

function deriveKey(password, salt, iterations) {
  return crypto.pbkdf2Sync(
    Buffer.from(password, 'utf8'),
    salt,
    iterations,
    KEY_LEN,
    'sha256',
  );
}

function readPassword(prompt) {
  return new Promise((resolve) => {
    const stdin  = process.stdin;
    const stdout = process.stdout;

    let rawMode = false;
    if (stdin.isTTY) {
      try { stdin.setRawMode(true); rawMode = true; } catch { /* ignore */ }
    }
    stdin.resume();
    stdin.setEncoding('utf8');
    stdout.write(prompt);

    let value = '';

    const cleanup = () => {
      stdin.removeListener('data', onData);
      if (rawMode) stdin.setRawMode(false);
      stdin.pause();
    };

    const onData = (chunk) => {
      for (const ch of chunk) {
        const code = ch.codePointAt(0);

        if (code === 3) { // Ctrl-C
          cleanup();
          stdout.write('\n');
          process.exit(130);
        }
        if (code === 13 || code === 10) { // Enter
          cleanup();
          stdout.write('\n');
          resolve(value);
          return;
        }
        if (code === 127 || code === 8) { // Backspace
          if (value.length > 0) {
            value = value.slice(0, -1);
            if (rawMode) stdout.write('\b \b');
          }
          continue;
        }
        value += ch;
        if (rawMode) stdout.write('*');
      }
    };

    stdin.on('data', onData);
  });
}

// ─── 加密 ────────────────────────────────────────────────────────────────────

function encryptFile(inPath, outPath, password) {
  const plaintext = fs.readFileSync(inPath);

  const salt  = crypto.randomBytes(SALT_LEN);
  const nonce = crypto.randomBytes(NONCE_LEN);

  const key    = deriveKey(password, salt, KDF_ITER);
  const cipher = crypto.createCipheriv(CIPHER, key, nonce);

  const ciphertext = Buffer.concat([cipher.update(plaintext), cipher.final()]);
  const tag        = cipher.getAuthTag();

  const container = {
    v:      1,
    alg:    CIPHER,
    kdf:    KDF_NAME,
    iter:   KDF_ITER,
    klen:   KEY_LEN,
    pwdesc: PASSWORD_DESC,
    salt:   salt.toString('base64'),
    nonce:  nonce.toString('base64'),
    tag:    tag.toString('base64'),
    data:   ciphertext.toString('base64'),
  };

  fs.writeFileSync(outPath, JSON.stringify(container), 'utf8');
}

// ─── 解密 ────────────────────────────────────────────────────────────────────

function decryptFile(inPath, outPath, password) {
  let c;
  try {
    c = JSON.parse(fs.readFileSync(inPath, 'utf8'));
  } catch {
    throw new Error('invalid container (not valid JSON)');
  }

  if (c.alg !== CIPHER)   throw new Error(`unsupported alg: ${c.alg}`);
  if (c.kdf !== KDF_NAME) throw new Error(`unsupported kdf: ${c.kdf}`);

  const salt  = Buffer.from(c.salt,  'base64');
  const nonce = Buffer.from(c.nonce, 'base64');
  const tag   = Buffer.from(c.tag,   'base64');
  const data  = Buffer.from(c.data,  'base64');

  if (salt.length  !== SALT_LEN)  throw new Error('invalid salt length');
  if (nonce.length !== NONCE_LEN) throw new Error('invalid nonce length');
  if (tag.length   !== TAG_LEN)   throw new Error('invalid tag length');

  const iterations = Number(c.iter);
  if (!Number.isInteger(iterations) || iterations <= 0) {
    throw new Error('invalid iterations');
  }

  const key = deriveKey(password, salt, iterations);
  const decipher = crypto.createDecipheriv(CIPHER, key, nonce);
  decipher.setAuthTag(tag);

  let plaintext;
  try {
    plaintext = Buffer.concat([decipher.update(data), decipher.final()]);
  } catch {
    throw new Error('decryption failed (wrong password or corrupted data)');
  }

  fs.writeFileSync(outPath, plaintext);
}

// ─── CLI ─────────────────────────────────────────────────────────────────────

function usage() {
  console.error(
`usage:
  node sealText.mjs enc <in> <out>
  node sealText.mjs dec <in> <out>`,
  );
  process.exit(2);
}

async function main() {
  const args = process.argv.slice(2);
  if (args.length !== 3) usage();

  const [cmd, inPath, outPath] = args;

  if (!fs.existsSync(inPath)) {
    console.error(`input not found: ${inPath}`);
    process.exit(1);
  }

  const envPass = passwordFromEnv();

  switch (cmd) {
    case 'enc': {
      let password;
      if (envPass !== null) {
        password = envPass;
      } else {
        password = generatePassword();
        console.log(password);
      }
      encryptFile(inPath, outPath, password);
      break;
    }
    case 'dec': {
      let password;
      if (envPass !== null) {
        password = envPass;
      } else {
        password = (await readPassword('Password: ')).trim();
        if (password.length === 0) {
          console.error('empty password');
          process.exit(1);
        }
      }
      decryptFile(inPath, outPath, password);
      break;
    }
    default:
      usage();
  }
}

main().catch((err) => {
  console.error(`error: ${err.message}`);
  process.exit(1);
});