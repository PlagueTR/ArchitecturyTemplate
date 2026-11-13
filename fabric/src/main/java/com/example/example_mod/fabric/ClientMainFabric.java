package com.example.example_mod.fabric;

import com.example.example_mod.ClientMain;

import net.fabricmc.api.ClientModInitializer;

public final class ClientMainFabric implements ClientModInitializer {

    @Override
    public void onInitializeClient() {
        ClientMain.init();
    }

}
