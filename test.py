
import asyncio
import aiosmtplib

from src.config.settings import settings


async def test_smtp():
    try:
        smtp = aiosmtplib.SMTP(
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            start_tls=True,
            timeout=20,
        )

        await smtp.connect()
        print("SMTP connection established.")

        await smtp.login(
            settings.smtp_username,
            settings.smtp_password,
        )
        print("SMTP authentication successful!")

        await smtp.quit()

    except Exception as exc:
        print(f"SMTP test failed: {type(exc).__name__}: {exc}")


if __name__ == "__main__":
    asyncio.run(test_smtp())
