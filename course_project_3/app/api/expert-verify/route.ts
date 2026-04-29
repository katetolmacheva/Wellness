import { NextResponse } from "next/server";

function appendIfExists(form: FormData, key: string, value: FormDataEntryValue | null) {
    if (value !== null) {
        form.append(key, value);
    }
}

function buildExpertVerifyForm(incomingForm: FormData) {
    const upstreamForm = new FormData();

    const educationDescription =
        incomingForm.get("education_description") ||
        incomingForm.get("educationDescription") ||
        incomingForm.get("diplomaInfo");

    const firstName =
        incomingForm.get("first_name") ||
        incomingForm.get("firstName");

    const lastName =
        incomingForm.get("last_name") ||
        incomingForm.get("lastName");

    const file =
        incomingForm.get("file") ||
        incomingForm.get("document");

    appendIfExists(upstreamForm, "education_description", educationDescription);
    appendIfExists(upstreamForm, "first_name", firstName);
    appendIfExists(upstreamForm, "last_name", lastName);
    appendIfExists(upstreamForm, "file", file);

    return {
        upstreamForm,
        debug: {
            keys: Array.from(incomingForm.keys()),
            education_description: educationDescription,
            first_name: firstName,
            last_name: lastName,
            hasFile: file instanceof File,
            file:
                file instanceof File
                    ? {
                        name: file.name,
                        type: file.type,
                        size: file.size,
                    }
                    : null,
        },
    };
}

export async function POST(req: Request) {
    try {
        const incomingForm = await req.formData();

        const { upstreamForm, debug } = buildExpertVerifyForm(incomingForm);

        console.log("EXPERT VERIFY INCOMING FORM:", debug);

        const primaryBase =
            process.env.EXPERT_API_URL ||
            process.env.CHAT_API_URL ||
            process.env.NEXT_PUBLIC_EXPERT_API_URL ||
            process.env.NEXT_PUBLIC_CHAT_API_URL ||
            "https://zealous-integrity-production-4287.up.railway.app";

        let upstream = await fetch(`${primaryBase}/expert/verify`, {
            method: "POST",
            body: upstreamForm,
            cache: "no-store",
        });

        if (upstream.status === 404 && primaryBase !== "http://localhost:8000") {
            const fallback = buildExpertVerifyForm(incomingForm);

            upstream = await fetch("http://localhost:8000/expert/verify", {
                method: "POST",
                body: fallback.upstreamForm,
                cache: "no-store",
            });
        }

        const text = await upstream.text();

        console.log("EXPERT VERIFY UPSTREAM RESPONSE:", {
            status: upstream.status,
            body: text,
        });

        const normalizedBody = (() => {
            if (!text) return "{}";

            try {
                JSON.parse(text);
                return text;
            } catch {
                return JSON.stringify({
                    detail: text.slice(0, 500),
                });
            }
        })();

        return new NextResponse(normalizedBody, {
            status: upstream.status,
            headers: { "Content-Type": "application/json" },
        });
    } catch (error) {
        console.error("EXPERT VERIFY PROXY CRASHED:", error);

        return NextResponse.json(
            {
                error: "expert verify proxy crashed",
                details: error instanceof Error ? error.message : "unknown",
            },
            { status: 502 }
        );
    }
}