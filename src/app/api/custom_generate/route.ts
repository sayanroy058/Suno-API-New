import { NextResponse, NextRequest } from "next/server";
import { cookies } from 'next/headers';
import { DEFAULT_MODEL, sunoApi } from "@/lib/SunoApi";
import { corsHeaders } from "@/lib/utils";

export const maxDuration = 60; // allow longer timeout for wait_audio == true
export const dynamic = "force-dynamic";

export async function POST(req: NextRequest) {
  if (req.method === 'POST') {
    try {
      const body = await req.json();
      const { prompt, tags, title, make_instrumental, model, wait_audio, negative_tags } = body;
      const audioInfo = await (await sunoApi((await cookies()).toString())).custom_generate(
        prompt, tags, title,
        Boolean(make_instrumental),
        model || DEFAULT_MODEL,
        Boolean(wait_audio),
        negative_tags
      );
      return new NextResponse(JSON.stringify(audioInfo), {
        status: 200,
        headers: {
          'Content-Type': 'application/json',
          ...corsHeaders
        }
      });
    } catch (error: any) {
      console.error('Error generating custom audio:', error);
      let errorDetail = 'Unknown error occurred';
      let statusCode = 500;

      if (error.response?.data?.detail) {
        errorDetail = error.response.data.detail;
        statusCode = error.response.status || 500;
      } else if (error.message) {
        errorDetail = error.message;
      }

      return new NextResponse(JSON.stringify({ error: errorDetail }), {
        status: statusCode,
        headers: {
          'Content-Type': 'application/json',
          ...corsHeaders
        }
      });
    }
  } else {
    return new NextResponse('Method Not Allowed', {
      headers: {
        Allow: 'POST',
        ...corsHeaders
      },
      status: 405
    });
  }
}

export async function OPTIONS(request: Request) {
  return new Response(null, {
    status: 200,
    headers: corsHeaders
  });
}
