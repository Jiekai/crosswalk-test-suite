package org.xwalk.embedded.api.sample;

import android.app.AlertDialog;
import android.graphics.Bitmap;
import android.os.Bundle;
import android.os.Message;
import android.widget.ImageView;
import android.widget.TextView;

import org.xwalk.core.XWalkActivity;
import org.xwalk.core.XWalkPreferences;
import org.xwalk.core.XWalkView;
import org.xwalk.core.XWalkUIClient;

public class OnIconAvailableOnReceivedIconActivity extends XWalkActivity {
    private XWalkView mXWalkView;
    private TextView mTitleText1;
    private TextView mTitleText2;
    private ImageView mFavicon;
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
    	super.onCreate(savedInstanceState);
    }

    @Override
    protected void onXWalkReady() {
    	StringBuffer mess = new StringBuffer();
        mess.append("Test Purpose: \n\n")
        .append("Verifies onIconAvailable and onReceivedIcon methods can be triggered when icon is available.\n\n")
        .append("Expected Result:\n\n")
        .append("1. Test passes if app show 'onIconAvailable'.\n")
        .append("2. Test passes if app show 'onReceivedIcon'.\n")
        .append("3. Test passes if app show a image of bird.");
        new  AlertDialog.Builder(this)
        .setTitle("Info" )
        .setMessage(mess.toString())
        .setPositiveButton("confirm" ,  null )
        .show();

        setContentView(R.layout.embedding_main);
        mXWalkView = (XWalkView) findViewById(R.id.xwalkview_embedding);
        mXWalkView.setUIClient(new TestXWalkUIClientBase(mXWalkView));

        XWalkPreferences.setValue(XWalkPreferences.SUPPORT_MULTIPLE_WINDOWS, true);
        XWalkPreferences.setValue(XWalkPreferences.REMOTE_DEBUGGING, true);
        XWalkPreferences.setValue(XWalkPreferences.JAVASCRIPT_CAN_OPEN_WINDOW, true);
        mTitleText1 = (TextView) findViewById(R.id.titletext1);
        mTitleText2 = (TextView) findViewById(R.id.titletext2);
        mFavicon = (ImageView) findViewById(R.id.imageView1);
        mXWalkView.load("file:///android_asset/window_icon.html", null);
    }

    class TestXWalkUIClientBase extends XWalkUIClient {

        public TestXWalkUIClientBase(XWalkView arg0) {
            super(arg0);
        }

        @Override
        public void onIconAvailable(XWalkView view, String url, Message msg) {
            mTitleText1.setText("onIconAvailable");
            msg.sendToTarget();
        }

        @Override
        public void onReceivedIcon(XWalkView view, String url, Bitmap icon) {
            mFavicon.setImageBitmap(icon);
            mTitleText2.setText("onReceivedIcon");
        }
    }
}
